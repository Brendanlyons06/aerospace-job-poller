CREATE TABLE IF NOT EXISTS companies (
    company TEXT PRIMARY KEY,
    slug TEXT,
    sector TEXT NOT NULL,
    careers_url TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS url TEXT NOT NULL DEFAULT '';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS sector TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS discipline TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS employment_type TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS work_mode TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS posted_at TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS closes_at TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS last_seen TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS closed_at TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS missed_polls INTEGER NOT NULL DEFAULT 0;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compensation_min NUMERIC;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compensation_max NUMERIC;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compensation_currency TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compensation_period TEXT;

UPDATE jobs SET last_seen = first_seen WHERE last_seen IS NULL;

CREATE TABLE IF NOT EXISTS job_locations (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    location_index INTEGER NOT NULL,
    label TEXT NOT NULL,
    city TEXT,
    state TEXT,
    country TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    PRIMARY KEY (company, job_id, location_index)
);

CREATE INDEX IF NOT EXISTS jobs_active_filter_idx
    ON jobs (closed_at, sector, discipline, work_mode);
CREATE INDEX IF NOT EXISTS job_locations_geo_idx
    ON job_locations (state, city);

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_locations ENABLE ROW LEVEL SECURITY;
