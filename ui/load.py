import psycopg2
from psycopg2.extras import execute_values
import sys
import traceback

DB_CONFIG = {
    "host": "sa.edumgt.co.kr",
    "port": 5432,
    "user": "postgres",
    "password": "star##!!5836",
    "dbname": "postgres"
}


def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("✅ Checking entity_flattened table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.entity_flattened (
            entity_id VARCHAR(255) PRIMARY KEY,
            schema VARCHAR(255),
            dataset VARCHAR(255),
            name VARCHAR(65535),
            alias VARCHAR(65535),
            first_name VARCHAR(65535),
            last_name VARCHAR(65535),
            birth_date VARCHAR(255),
            country VARCHAR(255),
            nationality VARCHAR(255),
            gender VARCHAR(255),
            address VARCHAR(65535),
            passport_number VARCHAR(255),
            id_number VARCHAR(255),
            source_url VARCHAR(65535),
            topics TEXT[]
        );
        """)

        print("🌀 Aggregating data from statement table...")
        sql = """
        SELECT
            canonical_id AS entity_id,
            MAX(schema) AS schema,
            MAX(dataset) AS dataset,
            MAX(CASE WHEN prop = 'name' THEN value END) AS name,

            STRING_AGG(DISTINCT NULLIF(CASE WHEN prop = 'alias' THEN value END, ''), ', ') AS alias,

            MAX(CASE WHEN prop = 'firstName' THEN value END) AS first_name,
            MAX(CASE WHEN prop = 'lastName' THEN value END) AS last_name,
            MAX(CASE WHEN prop = 'birthDate' THEN value END) AS birth_date,

            STRING_AGG(DISTINCT NULLIF(CASE WHEN prop = 'country' THEN value END, ''), ' · ') AS country,
            STRING_AGG(DISTINCT NULLIF(CASE WHEN prop = 'nationality' THEN value END, ''), ' · ') AS nationality,
            MAX(CASE WHEN prop = 'gender' THEN value END) AS gender,
            STRING_AGG(DISTINCT NULLIF(CASE WHEN prop = 'address' THEN value END, ''), ' · ') AS address,
            MAX(CASE WHEN prop = 'passportNumber' THEN value END) AS passport_number,
            MAX(CASE WHEN prop = 'id' THEN value END) AS id_number,
            MAX(CASE WHEN prop = 'sourceUrl' THEN value END) AS source_url,

            ARRAY_AGG(DISTINCT CASE WHEN prop = 'topics' THEN value END) FILTER (WHERE prop = 'topics') AS topics
        FROM public.statement
        GROUP BY canonical_id;
        """

        cur.execute(sql)
        rows = cur.fetchall()
        print(f"📦 Aggregated {len(rows)} entity records")

        print("🚀 Upserting into entity_flattened table...")
        insert_sql = """
        INSERT INTO public.entity_flattened (
            entity_id, schema, dataset, name, alias, first_name, last_name, birth_date, country,
            nationality, gender, address, passport_number, id_number, source_url, topics
        ) VALUES %s
        ON CONFLICT (entity_id)
        DO UPDATE SET
            schema = EXCLUDED.schema,
            dataset = EXCLUDED.dataset,
            name = EXCLUDED.name,
            alias = EXCLUDED.alias,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            birth_date = EXCLUDED.birth_date,
            country = EXCLUDED.country,
            nationality = EXCLUDED.nationality,
            gender = EXCLUDED.gender,
            address = EXCLUDED.address,
            passport_number = EXCLUDED.passport_number,
            id_number = EXCLUDED.id_number,
            source_url = EXCLUDED.source_url,
            topics = EXCLUDED.topics;
        """

        execute_values(cur, insert_sql, rows)
        conn.commit()
        print("✅ Batch process completed successfully!")

    except Exception as e:
        print("❌ Error during batch processing:")
        traceback.print_exc(file=sys.stdout)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("🔒 Connection closed.")


if __name__ == "__main__":
    main()
