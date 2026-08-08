"""SQLite persistent state for job watching, shared across every company.

Schema is keyed by (company, job_id) so the same database scales to hundreds
of companies without any per-company table. First sync for a company seeds
its currently-open jobs as "seen" without reporting them as new — otherwise
the first run of a brand new company would report its entire job board as
new postings.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jobs.db"

_SCHEMA = """
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
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SCHEMA)
    return conn


def sync_and_get_new(company: str, jobs: list[dict]) -> list[dict]:
    """Record every job as seen, return only the ones that are new since last sync.

    On a company's first-ever sync, seeds all current jobs as seen and
    returns [] (bootstrap — nothing to alert on yet).
    """
    conn = _connect()
    try:
        already_initialized = conn.execute(
            "SELECT 1 FROM companies_meta WHERE company = ?", (company,)
        ).fetchone() is not None

        existing_ids = {
            row[0]
            for row in conn.execute(
                "SELECT job_id FROM jobs WHERE company = ?", (company,)
            )
        }

        now = datetime.now(timezone.utc).isoformat()
        for job in jobs:
            conn.execute(
                "INSERT OR IGNORE INTO jobs (company, job_id, title, locations, first_seen) "
                "VALUES (?, ?, ?, ?, ?)",
                (company, job["id"], job["title"], ", ".join(job["locations"]), now),
            )

        if not already_initialized:
            conn.execute(
                "INSERT INTO companies_meta (company, initialized_at) VALUES (?, ?)",
                (company, now),
            )
            conn.commit()
            return []

        conn.commit()
        return [job for job in jobs if job["id"] not in existing_ids]
    finally:
        conn.close()
