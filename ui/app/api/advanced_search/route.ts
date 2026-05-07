import { NextRequest, NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({
  host: process.env.DB_HOST || "127.0.0.1",
  port: 5432,
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "password",
  database: process.env.DB_NAME || "dev",
});

export async function POST(req: NextRequest) {
  const { query, filters, page = 1, limit = 10 } = await req.json();
  const offset = (page - 1) * limit;
  const client = await pool.connect();

  try {
    const whereClauses: string[] = [];
    const params: any[] = [];

    // ✅ 이름 검색
    if (query && query.trim() !== "") {
      params.push(`%${query.toLowerCase()}%`);
      whereClauses.push(`LOWER(name) LIKE $${params.length}`);
    }

    // ✅ TYPE (schema)
    if (filters?.type?.length > 0) {
      const typeArray = Array.isArray(filters.type)
        ? filters.type
        : [filters.type];
      const placeholders = typeArray.map(
        (_: string, i: number) => `$${params.length + i + 1}`
      );
      params.push(...typeArray.map((t: string) => t.toLowerCase()));
      whereClauses.push(`LOWER(schema) IN (${placeholders.join(",")})`);
    }

    // ✅ DATASET (부분 일치)
    if (filters?.dataset?.length > 0) {
      const datasetArray = Array.isArray(filters.dataset)
        ? filters.dataset
        : [filters.dataset];
      const datasetConditions = datasetArray
        .map((_: string, i: number) => `LOWER(dataset) LIKE $${params.length + i + 1}`)
        .join(" OR ");
      params.push(...datasetArray.map((d: string) => `%${d.toLowerCase()}%`));
      whereClauses.push(`(${datasetConditions})`);
    }

    const whereSQL =
      whereClauses.length > 0 ? `WHERE ${whereClauses.join(" AND ")}` : "";

    const dataSql = `
      SELECT *
      FROM public.entity_flattened
      ${whereSQL}
      ORDER BY name
      LIMIT ${limit} OFFSET ${offset};
    `;
    const countSql = `
      SELECT COUNT(*) AS total
      FROM public.entity_flattened
      ${whereSQL};
    `;

    console.log("🟩 [ADVANCED SEARCH] =====================================================");
    console.log("📜 SQL (data):", dataSql.replace(/\s+/g, " ").trim());
    console.log("📜 SQL (count):", countSql.replace(/\s+/g, " ").trim());
    console.log("💾 Params:", JSON.stringify(params, null, 2));
    console.log("==========================================================================");

    const [dataRes, countRes] = await Promise.all([
      client.query(dataSql, params),
      client.query(countSql, params),
    ]);

    let dataRows = dataRes.rows;
    let total = Number(countRes.rows[0]?.total || 0);
    let totalPages = Math.ceil(total / limit);

    // ✅ Fallback: dataset 결과가 0건이면 schema-only 재검색
    if (total === 0 && filters?.dataset?.length > 0) {
      console.log("⚠️ No dataset match found — fallback to schema-only search");

      const fallbackParams: any[] = [];
      const fallbackClauses: string[] = [];

      // 1️⃣ 이름 조건
      if (query && query.trim() !== "") {
        fallbackParams.push(`%${query.toLowerCase()}%`);
        fallbackClauses.push(`LOWER(name) LIKE $${fallbackParams.length}`);
      }

      // 2️⃣ schema 조건
      if (filters?.type?.length > 0) {
        const typeArray = Array.isArray(filters.type)
          ? filters.type
          : [filters.type];
        const placeholders = typeArray.map(
          (_: string, i: number) => `$${fallbackParams.length + i + 1}`
        );
        fallbackParams.push(...typeArray.map((t: string) => t.toLowerCase()));
        fallbackClauses.push(`LOWER(schema) IN (${placeholders.join(",")})`);
      }

      const fallbackWhereSQL =
        fallbackClauses.length > 0 ? `WHERE ${fallbackClauses.join(" AND ")}` : "";

      const fallbackDataSql = `
        SELECT *
        FROM public.entity_flattened
        ${fallbackWhereSQL}
        ORDER BY name
        LIMIT ${limit} OFFSET ${offset};
      `;
      const fallbackCountSql = `
        SELECT COUNT(*) AS total
        FROM public.entity_flattened
        ${fallbackWhereSQL};
      `;

      console.log("🟨 [FALLBACK QUERY]");
      console.log("📜 SQL (data):", fallbackDataSql.replace(/\s+/g, " ").trim());
      console.log("💾 Params:", JSON.stringify(fallbackParams, null, 2));
      console.log("==========================================================================");

      const [fallbackDataRes, fallbackCountRes] = await Promise.all([
        client.query(fallbackDataSql, fallbackParams),
        client.query(fallbackCountSql, fallbackParams),
      ]);

      dataRows = fallbackDataRes.rows;
      total = Number(fallbackCountRes.rows[0]?.total || 0);
      totalPages = Math.ceil(total / limit);
    }

    // ✅ 통계
    const statsSql = `
      SELECT
        (SELECT COUNT(*) FROM public.entity_flattened) AS entity_count,
        (SELECT COUNT(DISTINCT dataset) FROM public.entity_flattened) AS source_count;
    `;
    const statsRes = await client.query(statsSql);

    return NextResponse.json({
      data: dataRows,
      pagination: { total, page, totalPages },
      stats: statsRes.rows[0],
    });
  } catch (err) {
    console.error("❌ DB error:", err);
    return NextResponse.json({ error: (err as Error).message }, { status: 500 });
  } finally {
    client.release();
  }
}
