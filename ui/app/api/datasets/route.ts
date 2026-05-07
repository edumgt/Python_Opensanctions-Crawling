// app/api/datasets/route.ts
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
  const code = searchParams.get("code")?.trim().toUpperCase();

  if (!code || code.length < 2) {
    return NextResponse.json({ error: "Missing or invalid code" }, { status: 400 });
  }

  try {
    const client = await pool.connect();

    // ✅ code 앞 2글자에 맞는 dataset 조회
    const sql = `
      SELECT dataset
      FROM public.entity_flattened
      WHERE dataset ILIKE $1 || '%'
      GROUP BY dataset
      ORDER BY dataset;
    `;
    const result = await client.query(sql, [code]);
    client.release();

    const datasets = result.rows.map((r) => r.dataset);
    console.log(`✅ [${code}] datasets:`, datasets.length);

    return NextResponse.json({ data: datasets });
  } catch (err: any) {
    console.error("❌ DB error in /api/datasets:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
