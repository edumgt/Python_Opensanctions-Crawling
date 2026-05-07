// app/api/types/route.ts
import { NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({
  host: process.env.DB_HOST || "127.0.0.1",
  port: 5432,
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "password",
  database: process.env.DB_NAME || "dev",
});

export async function GET() {
  try {
    const client = await pool.connect();
    const result = await client.query(`
      SELECT schema
      FROM public.entity_flattened
      WHERE schema IS NOT NULL AND schema <> ''
      GROUP BY schema
      ORDER BY schema;
    `);
    client.release();

    const schemas = result.rows.map((r) => r.schema);
    console.log("✅ Schema list:", schemas);
    return NextResponse.json({ data: schemas });
  } catch (err: any) {
    console.error("❌ DB error in /api/types:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
