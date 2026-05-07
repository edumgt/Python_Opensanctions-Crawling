// app/api/countries/route.ts
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
      SELECT 
        DISTINCT 
        SUBSTRING(e.dataset FROM 1 FOR 2) AS prefix,
        n.code,
        n.nation_kor
      FROM public.entity_flattened e
      JOIN public.nation_code n
        ON LOWER(SUBSTRING(e.dataset FROM 1 FOR 2)) = LOWER(n.code)
      WHERE e.dataset IS NOT NULL
      ORDER BY prefix;
    `);
    client.release();

    const nations = result.rows.map((r) => ({
      code: r.code,
      name: r.nation_kor,
    }));

    console.log("✅ Nation list:", nations.length, "items");
    return NextResponse.json({ data: nations });
  } catch (err: any) {
    console.error("❌ DB error in /api/countries:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
