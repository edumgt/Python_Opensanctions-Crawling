import { NextRequest, NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({
  host: process.env.DB_HOST || "127.0.0.1",
  port: 5432,
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "password",
  database: process.env.DB_NAME || "dev",
});

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get("q")?.trim().toLowerCase() || "";
  const page = Number(searchParams.get("page") || "1");
  const limit = Number(searchParams.get("limit") || "10");
  const offset = (page - 1) * limit;

  const client = await pool.connect();
  try {
    // ✅ 통계 항상 반환
    const statsSql = `
      SELECT
        (SELECT COUNT(*) FROM public.entity_flattened) AS entity_count,
        (SELECT COUNT(DISTINCT dataset) FROM public.entity_flattened WHERE dataset IS NOT NULL) AS source_count;
    `;

    const statsRes = await client.query(statsSql);
    const stats = statsRes.rows[0];

    // ✅ 검색어 없을 때: 목록은 비우되 통계만 반환
    if (!q) {
      return NextResponse.json({
        data: [],
        pagination: { total: 0, page, totalPages: 0 },
        stats,
      });
    }

    const baseSql = `
      FROM public.entity_flattened
      WHERE (
        LOWER(name) LIKE $1 OR
        LOWER(alias) LIKE $1 OR
        LOWER(entity_id) LIKE $1 OR
        LOWER(address) LIKE $1
      )
    `;
    const countSql = `SELECT COUNT(*) AS total ${baseSql}`;
    const dataSql = `
      SELECT
        entity_id, schema, name, alias, first_name, last_name,
        birth_date, gender, nationality, country, address,
        passport_number, id_number, source_url,
        CASE
          WHEN topics IS NULL OR trim(topics::text) = '' THEN ARRAY[]::text[]
          WHEN left(topics::text, 1) = '{' AND right(topics::text, 1) = '}' THEN topics::text[]
          ELSE string_to_array(replace(topics::text, '"', ''), ',')
        END AS topics
      ${baseSql}
      ORDER BY name
      LIMIT $2 OFFSET $3;
    `;

    const countRes = await client.query(countSql, [`%${q}%`]);
    const total = Number(countRes.rows[0]?.total || 0);
    const totalPages = Math.ceil(total / limit);
    const dataRes = await client.query(dataSql, [`%${q}%`, limit, offset]);

    return NextResponse.json({
      data: dataRes.rows,
      pagination: { total, page, totalPages },
      stats,
    });
  } catch (err) {
    console.error("❌ Query failed:", err);
    return NextResponse.json({ error: (err as Error).message }, { status: 500 });
  } finally {
    client.release();
  }
}
