-- =========================================================
-- Drop existing tables (clean reset)
-- =========================================================

DROP TABLE IF EXISTS storm_events_audit;
DROP TABLE IF EXISTS storm_events_details_invalid;
DROP TABLE IF EXISTS storm_events_details_cleaned;
DROP TABLE IF EXISTS storm_events_details;

-- =========================================================
-- 1. Create tables (with full column list, QUOTED)
-- =========================================================

-- Raw staging table (from CSV/JSON)
CREATE TABLE storm_events_details (
    "BEGIN_YEARMONTH"     integer,
    "BEGIN_DAY"           integer,
    "BEGIN_TIME"          integer,
    "END_YEARMONTH"       integer,
    "END_DAY"             integer,
    "END_TIME"            integer,
    "EPISODE_ID"          bigint,
    "EVENT_ID"            bigint,
    "STATE"               text,
    "STATE_FIPS"          text,
    "YEAR"                integer,
    "MONTH_NAME"          text,
    "EVENT_TYPE"          text,
    "CZ_TYPE"             text,
    "CZ_FIPS"             text,
    "CZ_NAME"             text,
    "WFO"                 text,
    "BEGIN_DATE_TIME"     timestamp,
    "CZ_TIMEZONE"         text,
    "END_DATE_TIME"       timestamp,
    "INJURIES_DIRECT"     integer,
    "INJURIES_INDIRECT"   integer,
    "DEATHS_DIRECT"       integer,
    "DEATHS_INDIRECT"     integer,
    "DAMAGE_PROPERTY"     numeric,
    "DAMAGE_CROPS"        numeric,
    "SOURCE"              text,
    "MAGNITUDE"           numeric,
    "MAGNITUDE_TYPE"      text,
    "FLOOD_CAUSE"         text,
    "CATEGORY"            text,
    "TOR_F_SCALE"         text,
    "TOR_LENGTH"          numeric,
    "TOR_WIDTH"           numeric,
    "TOR_OTHER_WFO"       text,
    "TOR_OTHER_CZ_STATE"  text,
    "TOR_OTHER_CZ_FIPS"   text,
    "TOR_OTHER_CZ_NAME"   text,
    "BEGIN_RANGE"         numeric,
    "BEGIN_AZIMUTH"       text,
    "BEGIN_LOCATION"      text,
    "END_RANGE"           numeric,
    "END_AZIMUTH"         text,
    "END_LOCATION"        text,
    "BEGIN_LAT"           double precision,
    "BEGIN_LON"           double precision,
    "END_LAT"             double precision,
    "END_LON"             double precision,
    "EPISODE_NARRATIVE"   text,
    "EVENT_NARRATIVE"     text,
    "DATA_SOURCE"         text
);

-- Cleaned table:
-- Same as raw, but WITHOUT:
-- TOR_OTHER_WFO, TOR_OTHER_CZ_FIPS, TOR_OTHER_CZ_STATE, TOR_OTHER_CZ_NAME,
-- TOR_WIDTH, TOR_LENGTH, TOR_F_SCALE, EVENT_NARRATIVE, EPISODE_NARRATIVE,
-- CATEGORY, DATA_SOURCE
CREATE TABLE storm_events_details_cleaned (
    "BEGIN_YEARMONTH"     integer,
    "BEGIN_DAY"           integer,
    "BEGIN_TIME"          integer,
    "END_YEARMONTH"       integer,
    "END_DAY"             integer,
    "END_TIME"            integer,
    "EPISODE_ID"          bigint,
    "EVENT_ID"            bigint,
    "STATE"               text,
    "STATE_FIPS"          text,
    "YEAR"                integer,
    "MONTH_NAME"          text,
    "EVENT_TYPE"          text,
    "CZ_TYPE"             text,
    "CZ_FIPS"             text,
    "CZ_NAME"             text,
    "WFO"                 text,
    "BEGIN_DATE_TIME"     timestamp,
    "CZ_TIMEZONE"         text,
    "END_DATE_TIME"       timestamp,
    "INJURIES_DIRECT"     integer,
    "INJURIES_INDIRECT"   integer,
    "DEATHS_DIRECT"       integer,
    "DEATHS_INDIRECT"     integer,
    "DAMAGE_PROPERTY"     numeric NOT NULL DEFAULT 0,
    "DAMAGE_CROPS"        numeric NOT NULL DEFAULT 0,
    "SOURCE"              text,
    "MAGNITUDE"           numeric NOT NULL DEFAULT 0,
    "MAGNITUDE_TYPE"      text NOT NULL DEFAULT 'N/A',
    "FLOOD_CAUSE"         text NOT NULL DEFAULT 'N/A',
    "BEGIN_RANGE"         numeric,
    "BEGIN_AZIMUTH"       text,
    "BEGIN_LOCATION"      text,
    "END_RANGE"           numeric,
    "END_AZIMUTH"         text,
    "END_LOCATION"        text,
    "BEGIN_LAT"           double precision NOT NULL,
    "BEGIN_LON"           double precision NOT NULL,
    "END_LAT"             double precision NOT NULL,
    "END_LON"             double precision NOT NULL
);

-- Invalid rows table (rows where all coord columns are NULL)
-- Keep full schema like staging table
CREATE TABLE storm_events_details_invalid (
    "BEGIN_YEARMONTH"     integer,
    "BEGIN_DAY"           integer,
    "BEGIN_TIME"          integer,
    "END_YEARMONTH"       integer,
    "END_DAY"             integer,
    "END_TIME"            integer,
    "EPISODE_ID"          bigint,
    "EVENT_ID"            bigint,
    "STATE"               text,
    "STATE_FIPS"          text,
    "YEAR"                integer,
    "MONTH_NAME"          text,
    "EVENT_TYPE"          text,
    "CZ_TYPE"             text,
    "CZ_FIPS"             text,
    "CZ_NAME"             text,
    "WFO"                 text,
    "BEGIN_DATE_TIME"     timestamp,
    "CZ_TIMEZONE"         text,
    "END_DATE_TIME"       timestamp,
    "INJURIES_DIRECT"     integer,
    "INJURIES_INDIRECT"   integer,
    "DEATHS_DIRECT"       integer,
    "DEATHS_INDIRECT"     integer,
    "DAMAGE_PROPERTY"     numeric,
    "DAMAGE_CROPS"        numeric,
    "SOURCE"              text,
    "MAGNITUDE"           numeric,
    "MAGNITUDE_TYPE"      text,
    "FLOOD_CAUSE"         text,
    "CATEGORY"            text,
    "TOR_F_SCALE"         text,
    "TOR_LENGTH"          numeric,
    "TOR_WIDTH"           numeric,
    "TOR_OTHER_WFO"       text,
    "TOR_OTHER_CZ_STATE"  text,
    "TOR_OTHER_CZ_FIPS"   text,
    "TOR_OTHER_CZ_NAME"   text,
    "BEGIN_RANGE"         numeric,
    "BEGIN_AZIMUTH"       text,
    "BEGIN_LOCATION"      text,
    "END_RANGE"           numeric,
    "END_AZIMUTH"         text,
    "END_LOCATION"        text,
    "BEGIN_LAT"           double precision,
    "BEGIN_LON"           double precision,
    "END_LAT"             double precision,
    "END_LON"             double precision,
    "EPISODE_NARRATIVE"   text,
    "EVENT_NARRATIVE"     text,
    "DATA_SOURCE"         text
);

-- Audit table (keep simple, unquoted lowercase)
CREATE TABLE storm_events_audit (
    audit_id      bigserial PRIMARY KEY,
    table_name    text NOT NULL,
    operation     text NOT NULL,   -- 'INSERT', 'UPDATE', 'DELETE', 'DUPLICATE_INSERT'
    event_id      bigint,
    changed_at    timestamptz NOT NULL DEFAULT now(),
    old_row       jsonb,
    new_row       jsonb
);

-- =========================================================
-- 2. Change logging function
-- =========================================================

CREATE OR REPLACE FUNCTION log_storm_events_changes()
RETURNS trigger AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO storm_events_audit (table_name, operation, event_id, new_row)
        VALUES (TG_TABLE_NAME, TG_OP, NEW."EVENT_ID", to_jsonb(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO storm_events_audit (table_name, operation, event_id, old_row, new_row)
        VALUES (TG_TABLE_NAME, TG_OP, NEW."EVENT_ID", to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO storm_events_audit (table_name, operation, event_id, old_row)
        VALUES (TG_TABLE_NAME, TG_OP, OLD."EVENT_ID", to_jsonb(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- 3. Duplicate prevention function:
--    BEFORE INSERT:
--      - If same EVENT_ID exists in the same table:
--          * log DUPLICATE_INSERT into storm_events_audit
--          * skip the insert (return NULL)
-- =========================================================

CREATE OR REPLACE FUNCTION prevent_duplicate_event_id()
RETURNS trigger AS $$
DECLARE
    existing_row jsonb;
BEGIN
    -- Allow rows with NULL EVENT_ID
    IF NEW."EVENT_ID" IS NULL THEN
        RETURN NEW;
    END IF;

    -- Look for an existing row with the same EVENT_ID in this table
    EXECUTE format(
        'SELECT to_jsonb(t) FROM %I t WHERE "EVENT_ID" = $1 LIMIT 1',
        TG_TABLE_NAME
    )
    INTO existing_row
    USING NEW."EVENT_ID";

    IF existing_row IS NOT NULL THEN
        INSERT INTO storm_events_audit (table_name, operation, event_id, old_row, new_row)
        VALUES (TG_TABLE_NAME, 'DUPLICATE_INSERT', NEW."EVENT_ID", existing_row, to_jsonb(NEW));

        -- Skip the insert
        RETURN NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- 4. Attach triggers (logging + duplicate prevention)
-- =========================================================

-- storm_events_details: log changes + prevent duplicates
CREATE TRIGGER trg_log_details
AFTER INSERT OR UPDATE OR DELETE ON storm_events_details
FOR EACH ROW EXECUTE FUNCTION log_storm_events_changes();

CREATE TRIGGER trg_dup_details
BEFORE INSERT ON storm_events_details
FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_event_id();

-- storm_events_details_cleaned: log changes + prevent duplicates
CREATE TRIGGER trg_log_cleaned
AFTER INSERT OR UPDATE OR DELETE ON storm_events_details_cleaned
FOR EACH ROW EXECUTE FUNCTION log_storm_events_changes();

CREATE TRIGGER trg_dup_cleaned
BEFORE INSERT ON storm_events_details_cleaned
FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_event_id();

-- storm_events_details_invalid: log changes + prevent duplicates
CREATE TRIGGER trg_log_invalid
AFTER INSERT OR UPDATE OR DELETE ON storm_events_details_invalid
FOR EACH ROW EXECUTE FUNCTION log_storm_events_changes();

CREATE TRIGGER trg_dup_invalid
BEFORE INSERT ON storm_events_details_invalid
FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_event_id();
