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
  const sources = searchParams.get("sources");

  if (!sources) {
    return NextResponse.json({
      message: "Add ?sources=true to get data sources list.",
    });
  }

  const client = await pool.connect();
  try {
    // ✅ dataset과 count만 집계
    const sql = `
      SELECT 
        dataset,
        COUNT(*) AS count
      FROM public.entity_flattened
      GROUP BY dataset
      ORDER BY count DESC;
    `;
    const { rows } = await client.query(sql);
    return NextResponse.json({ sources: rows });
  } catch (err) {
    console.error("❌ DB error:", err);
    return NextResponse.json({ error: "DB query failed" }, { status: 500 });
  } finally {
    client.release();
  }
}
