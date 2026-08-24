CREATE TABLE IF NOT EXISTS jobs (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    title TEXT NOT NULL,
    locations TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    PRIMARY KEY (company, job_id)
);

CREATE TABLE IF NOT EXISTS companies_meta (
    company TEXT PRIMARY KEY,
    initialized_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_outbox (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    title TEXT NOT NULL,
    locations TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    delivered_at TEXT,
    PRIMARY KEY (company, job_id)
);

CREATE TABLE IF NOT EXISTS company_health (
    company TEXT PRIMARY KEY,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    consecutive_zero INTEGER NOT NULL DEFAULT 0,
    last_success TEXT,
    last_failure TEXT,
    last_error TEXT,
    last_job_count INTEGER
);

CREATE TABLE IF NOT EXISTS system_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

ALTER TABLE schema_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies_meta ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_meta ENABLE ROW LEVEL SECURITY;
