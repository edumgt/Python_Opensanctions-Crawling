-- Auto-generated from db_table_spec.xlsx
SET client_min_messages = WARNING;
SET standard_conforming_strings = on;

-- Table: cache
CREATE TABLE IF NOT EXISTS public."cache" (
  "key" varchar PRIMARY KEY,
  "text" varchar,
  "dataset" varchar NOT NULL,
  "timestamp" timestamp
);

-- Table: entity_flattened
CREATE TABLE IF NOT EXISTS public."entity_flattened" (
  "entity_id" varchar(255) PRIMARY KEY,
  "schema" varchar(255),
  "dataset" varchar(255),
  "name" varchar(65535),
  "alias" varchar(65535),
  "first_name" varchar(65535),
  "last_name" varchar(65535),
  "birth_date" varchar(255),
  "country" varchar(255),
  "nationality" varchar(255),
  "gender" varchar(255),
  "address" varchar(65535),
  "passport_number" varchar(255),
  "id_number" varchar(255),
  "source_url" varchar(65535),
  "topics" varchar(2000)
);

-- Table: nation_code
CREATE TABLE IF NOT EXISTS public."nation_code" (
  "code" varchar(10) PRIMARY KEY,
  "nation_kor" varchar(100),
  "count" bigint
);

-- Table: position
CREATE TABLE IF NOT EXISTS public."position" (
  "id" serial PRIMARY KEY,
  "entity_id" varchar(255) NOT NULL,
  "caption" varchar(65535) NOT NULL,
  "countries" json NOT NULL,
  "is_pep" boolean,
  "topics" json NOT NULL,
  "dataset" varchar(65535) NOT NULL,
  "created_at" timestamp NOT NULL,
  "modified_at" timestamp,
  "modified_by" varchar(255),
  "deleted_at" timestamp
);

-- Table: program
CREATE TABLE IF NOT EXISTS public."program" (
  "id" serial PRIMARY KEY,
  "key" varchar(255) UNIQUE,
  "title" varchar(65535),
  "url" varchar(65535)
);

-- Table: resolver
CREATE TABLE IF NOT EXISTS public."resolver" (
  "id" serial PRIMARY KEY,
  "target" varchar(512),
  "source" varchar(512),
  "judgement" varchar(14) NOT NULL,
  "score" double precision,
  "user" varchar(512) NOT NULL,
  "created_at" varchar(28),
  "deleted_at" varchar(28)
);

-- Table: review
CREATE TABLE IF NOT EXISTS public."review" (
  "id" serial PRIMARY KEY,
  "key" varchar(255) NOT NULL,
  "dataset" varchar(255) NOT NULL,
  "extraction_schema" json NOT NULL,
  "source_value" varchar(1048576),
  "source_mime_type" varchar(65535),
  "source_label" varchar(65535),
  "source_url" varchar(65535),
  "accepted" boolean NOT NULL,
  "crawler_version" integer NOT NULL,
  "original_extraction" json NOT NULL,
  "origin" varchar(65535) NOT NULL,
  "extracted_data" json NOT NULL,
  "last_seen_version" varchar(255) NOT NULL,
  "modified_at" timestamp NOT NULL,
  "modified_by" varchar(255) NOT NULL,
  "deleted_at" timestamp
);

-- Table: statement
CREATE TABLE IF NOT EXISTS public."statement" (
  "id" varchar(255) PRIMARY KEY,
  "entity_id" varchar(255) NOT NULL,
  "canonical_id" varchar(255) NOT NULL,
  "prop" varchar(255) NOT NULL,
  "prop_type" varchar(255) NOT NULL,
  "schema" varchar(255) NOT NULL,
  "value" varchar(65535) NOT NULL,
  "original_value" varchar(65535),
  "dataset" varchar(255),
  "origin" varchar(255),
  "lang" varchar(255),
  "external" boolean NOT NULL,
  "first_seen" timestamp,
  "last_seen" timestamp
);
-- Column comments (English)
COMMENT ON COLUMN public."cache"."key" IS 'Cache key';
COMMENT ON COLUMN public."cache"."text" IS 'Cached text data';
COMMENT ON COLUMN public."cache"."dataset" IS 'Dataset name';
COMMENT ON COLUMN public."cache"."timestamp" IS 'Cache created/updated timestamp';

COMMENT ON COLUMN public."entity_flattened"."entity_id" IS 'Entity identifier';
COMMENT ON COLUMN public."entity_flattened"."schema" IS 'Entity schema type';
COMMENT ON COLUMN public."entity_flattened"."dataset" IS 'Source dataset';
COMMENT ON COLUMN public."entity_flattened"."name" IS 'Name';
COMMENT ON COLUMN public."entity_flattened"."alias" IS 'Alias';
COMMENT ON COLUMN public."entity_flattened"."first_name" IS 'First name';
COMMENT ON COLUMN public."entity_flattened"."last_name" IS 'Last name';
COMMENT ON COLUMN public."entity_flattened"."birth_date" IS 'Date of birth';
COMMENT ON COLUMN public."entity_flattened"."country" IS 'Country code';
COMMENT ON COLUMN public."entity_flattened"."nationality" IS 'Nationality';
COMMENT ON COLUMN public."entity_flattened"."gender" IS 'Gender';
COMMENT ON COLUMN public."entity_flattened"."address" IS 'Address';
COMMENT ON COLUMN public."entity_flattened"."passport_number" IS 'Passport number';
COMMENT ON COLUMN public."entity_flattened"."id_number" IS 'ID number';
COMMENT ON COLUMN public."entity_flattened"."source_url" IS 'Source URL';
COMMENT ON COLUMN public."entity_flattened"."topics" IS 'Related topics list';

COMMENT ON COLUMN public."nation_code"."code" IS 'Country code';
COMMENT ON COLUMN public."nation_code"."nation_kor" IS 'Country name (Korean)';
COMMENT ON COLUMN public."nation_code"."count" IS 'Entity count / statistic value';

COMMENT ON COLUMN public."position"."id" IS 'Primary ID';
COMMENT ON COLUMN public."position"."entity_id" IS 'Related entity ID';
COMMENT ON COLUMN public."position"."caption" IS 'Position/role title';
COMMENT ON COLUMN public."position"."countries" IS 'Related country information';
COMMENT ON COLUMN public."position"."is_pep" IS 'Is PEP (Politically Exposed Person)';
COMMENT ON COLUMN public."position"."topics" IS 'Related topic information';
COMMENT ON COLUMN public."position"."dataset" IS 'Dataset name';
COMMENT ON COLUMN public."position"."created_at" IS 'Created at';
COMMENT ON COLUMN public."position"."modified_at" IS 'Modified at';
COMMENT ON COLUMN public."position"."modified_by" IS 'Modified by';
COMMENT ON COLUMN public."position"."deleted_at" IS 'Deleted at';

COMMENT ON COLUMN public."program"."id" IS 'Primary ID';
COMMENT ON COLUMN public."program"."key" IS 'Program key';
COMMENT ON COLUMN public."program"."title" IS 'Program title';
COMMENT ON COLUMN public."program"."url" IS 'Program URL';

COMMENT ON COLUMN public."resolver"."id" IS 'Primary ID';
COMMENT ON COLUMN public."resolver"."target" IS 'Target value';
COMMENT ON COLUMN public."resolver"."source" IS 'Source';
COMMENT ON COLUMN public."resolver"."judgement" IS 'Judgement (duplicate/match/etc.)';
COMMENT ON COLUMN public."resolver"."score" IS 'Similarity score';
COMMENT ON COLUMN public."resolver"."user" IS 'Operator';
COMMENT ON COLUMN public."resolver"."created_at" IS 'Created time';
COMMENT ON COLUMN public."resolver"."deleted_at" IS 'Deleted time';

COMMENT ON COLUMN public."review"."id" IS 'Primary ID';
COMMENT ON COLUMN public."review"."key" IS 'Review key';
COMMENT ON COLUMN public."review"."dataset" IS 'Dataset name';
COMMENT ON COLUMN public."review"."extraction_schema" IS 'Extraction schema structure';
COMMENT ON COLUMN public."review"."source_value" IS 'Raw source data';
COMMENT ON COLUMN public."review"."source_mime_type" IS 'Source MIME type';
COMMENT ON COLUMN public."review"."source_label" IS 'Source label';
COMMENT ON COLUMN public."review"."source_url" IS 'Source URL';
COMMENT ON COLUMN public."review"."accepted" IS 'Accepted flag';
COMMENT ON COLUMN public."review"."crawler_version" IS 'Crawler version';
COMMENT ON COLUMN public."review"."original_extraction" IS 'Original extraction data';
COMMENT ON COLUMN public."review"."origin" IS 'Data origin';
COMMENT ON COLUMN public."review"."extracted_data" IS 'Extracted/transformed data';
COMMENT ON COLUMN public."review"."last_seen_version" IS 'Last seen version';
COMMENT ON COLUMN public."review"."modified_at" IS 'Modified at';
COMMENT ON COLUMN public."review"."modified_by" IS 'Modified by';
COMMENT ON COLUMN public."review"."deleted_at" IS 'Deleted at';

COMMENT ON COLUMN public."statement"."id" IS 'Statement ID';
COMMENT ON COLUMN public."statement"."entity_id" IS 'Related entity ID';
COMMENT ON COLUMN public."statement"."canonical_id" IS 'Canonical ID';
COMMENT ON COLUMN public."statement"."prop" IS 'Property name';
COMMENT ON COLUMN public."statement"."prop_type" IS 'Property type';
COMMENT ON COLUMN public."statement"."schema" IS 'Schema name';
COMMENT ON COLUMN public."statement"."value" IS 'Property value';
COMMENT ON COLUMN public."statement"."original_value" IS 'Original value';
COMMENT ON COLUMN public."statement"."dataset" IS 'Source dataset';
COMMENT ON COLUMN public."statement"."origin" IS 'Origin';
COMMENT ON COLUMN public."statement"."lang" IS 'Language';
COMMENT ON COLUMN public."statement"."external" IS 'External data flag';
COMMENT ON COLUMN public."statement"."first_seen" IS 'First seen timestamp';
COMMENT ON COLUMN public."statement"."last_seen" IS 'Last seen timestamp';
