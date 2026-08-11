"""SQLite persistent state for job watching, shared across every company.

Schema is keyed by (company, job_id) so the same database scales to hundreds
of companies without any per-company table. First sync for a company seeds
its currently-open jobs as "seen" without reporting them as new — otherwise
the first run of a brand new company would report its entire job board as
new postings.

`watch.py` opens one connection via `connect()` and passes it through the
serial diff loop — opening per-company connections (and re-running the
schema script each time) was pure overhead. `sync_and_get_new()` still opens
its own connection when called without one, for tests and one-off use.

Rows track `last_seen` so postings that vanished long ago can be pruned;
recently-closed jobs are deliberately kept, because a posting that
disappears and reappears within the window must not re-alert.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jobs.db"

# Prune rows this long after they last appeared on their board. Long on
# purpose: postings sometimes vanish and come back, and re-alerting on a
# reappearance is worse than carrying a few stale rows.
PRUNE_AFTER_DAYS = 180

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    title TEXT NOT NULL,
    locations TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    PRIMARY KEY (company, job_id)
);

CREATE TABLE IF NOT EXISTS companies_meta (
    company TEXT PRIMARY KEY,
    initialized_at TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    """Open the shared database, creating or migrating the schema as needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SCHEMA)
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring a pre-`last_seen` database up to the current schema, idempotently."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    if "last_seen" not in columns:
        conn.execute("ALTER TABLE jobs ADD COLUMN last_seen TEXT")
    conn.execute("UPDATE jobs SET last_seen = first_seen WHERE last_seen IS NULL")
    conn.commit()


def sync_and_get_new(
    company: str, jobs: list[dict], conn: sqlite3.Connection | None = None
) -> list[dict]:
    """Record every job as seen, return only the ones that are new since last sync.

    On a company's first-ever sync, seeds all current jobs as seen and
    returns [] (bootstrap — nothing to alert on yet).

    Pass ``conn`` to reuse one connection across companies (watch.py does);
    without it, a private connection is opened and closed per call.
    """
    owns_conn = conn is None
    if owns_conn:
        conn = connect()
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
        conn.executemany(
            "INSERT OR IGNORE INTO jobs (company, job_id, title, locations, first_seen, last_seen) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                (company, job["id"], job["title"], ", ".join(job["locations"]), now, now)
                for job in jobs
            ],
        )
        # Jobs still on the board stay fresh; rows that stop matching here
        # age out via prune_stale().
        conn.executemany(
            "UPDATE jobs SET last_seen = ? WHERE company = ? AND job_id = ?",
            [(now, company, job["id"]) for job in jobs],
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
        if owns_conn:
            conn.close()


def prune_stale(
    conn: sqlite3.Connection, days: int = PRUNE_AFTER_DAYS
) -> int:
    """Delete rows for postings unseen for ``days``; return how many went.

    ISO-8601 UTC timestamps compare correctly as strings, so this is a plain
    lexicographic cutoff.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cursor = conn.execute("DELETE FROM jobs WHERE last_seen < ?", (cutoff,))
    conn.commit()
    return cursor.rowcount
