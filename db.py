"""SQLite persistent state for job watching, shared across every company.

Schema is keyed by (company, job_id) so the same database scales to hundreds
of companies without any per-company table. First sync for a company seeds
its currently-open jobs as "seen" without reporting them as new — otherwise
the first run of a brand new company would report its entire job board as
new postings.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
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
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SCHEMA)
    return conn


def sync_and_get_new(company: str, jobs: list[dict]) -> list[dict]:
    """Record jobs and return every undelivered alert for this company.

    On a company's first-ever sync, seeds all current jobs as seen and
    returns [] (bootstrap — nothing to alert on yet). After initialization,
    newly discovered jobs enter a durable outbox. A failed email therefore
    remains pending and is retried on a later poll instead of being lost.
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

        for job in jobs:
            if job["id"] in existing_ids:
                continue
            conn.execute(
                "INSERT OR IGNORE INTO notification_outbox "
                "(company, job_id, title, locations, url, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    company,
                    job["id"],
                    job["title"],
                    json.dumps(job["locations"]),
                    job.get("url", ""),
                    now,
                ),
            )

        conn.commit()
        rows = conn.execute(
            "SELECT job_id, title, locations, url FROM notification_outbox "
            "WHERE company = ? AND delivered_at IS NULL ORDER BY created_at, job_id",
            (company,),
        ).fetchall()
        return [
            {
                "id": job_id,
                "title": title,
                "locations": json.loads(locations),
                "url": url,
            }
            for job_id, title, locations, url in rows
        ]
    finally:
        conn.close()


def mark_notification_delivered(company: str, job_id: str) -> None:
    """Mark an outbox item delivered so later polls do not resend it."""
    conn = _connect()
    try:
        conn.execute(
            "UPDATE notification_outbox SET delivered_at = ?, last_error = NULL "
            "WHERE company = ? AND job_id = ?",
            (datetime.now(timezone.utc).isoformat(), company, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def mark_notification_failed(company: str, job_id: str, error: str) -> None:
    """Record a failed attempt while leaving the outbox item pending."""
    conn = _connect()
    try:
        conn.execute(
            "UPDATE notification_outbox "
            "SET attempts = attempts + 1, last_error = ? "
            "WHERE company = ? AND job_id = ?",
            (error[:1000], company, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def record_poll_failure(company: str, error: str) -> tuple[int, bool]:
    """Record a board failure and say whether it just reached alert threshold."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT consecutive_failures FROM company_health WHERE company = ?",
            (company,),
        ).fetchone()
        count = (row[0] if row else 0) + 1
        conn.execute(
            "INSERT INTO company_health "
            "(company, consecutive_failures, last_failure, last_error) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(company) DO UPDATE SET "
            "consecutive_failures = excluded.consecutive_failures, "
            "last_failure = excluded.last_failure, last_error = excluded.last_error",
            (company, count, datetime.now(timezone.utc).isoformat(), error[:1000]),
        )
        conn.commit()
        return count, count == 3
    finally:
        conn.close()


def record_poll_success(company: str, job_count: int) -> tuple[bool, int]:
    """Record a successful board poll and return (recovered, zero streak)."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT consecutive_failures, consecutive_zero "
            "FROM company_health WHERE company = ?",
            (company,),
        ).fetchone()
        previous_failures, previous_zero = row or (0, 0)
        zero_count = previous_zero + 1 if job_count == 0 else 0
        conn.execute(
            "INSERT INTO company_health "
            "(company, consecutive_failures, consecutive_zero, last_success, "
            "last_failure, last_error, last_job_count) "
            "VALUES (?, 0, ?, ?, NULL, NULL, ?) "
            "ON CONFLICT(company) DO UPDATE SET "
            "consecutive_failures = 0, consecutive_zero = excluded.consecutive_zero, "
            "last_success = excluded.last_success, last_error = NULL, "
            "last_job_count = excluded.last_job_count",
            (
                company,
                zero_count,
                datetime.now(timezone.utc).isoformat(),
                job_count,
            ),
        )
        conn.commit()
        return previous_failures >= 3, zero_count
    finally:
        conn.close()


def health_snapshot() -> list[dict]:
    """Return company health rows for summaries and diagnostics."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT company, consecutive_failures, consecutive_zero, last_success, "
            "last_failure, last_error, last_job_count "
            "FROM company_health ORDER BY company"
        ).fetchall()
        return [
            {
                "company": company,
                "consecutive_failures": failures,
                "consecutive_zero": zero,
                "last_success": success,
                "last_failure": failure,
                "last_error": error,
                "last_job_count": count,
            }
            for company, failures, zero, success, failure, error, count in rows
        ]
    finally:
        conn.close()


def weekly_summary_due(*, now: datetime | None = None) -> bool:
    """Return true weekly, establishing a baseline without an immediate email."""
    now = now or datetime.now(timezone.utc)
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT value FROM system_meta WHERE key = 'weekly_health_summary'"
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO system_meta (key, value) VALUES (?, ?)",
                ("weekly_health_summary", now.isoformat()),
            )
            conn.commit()
            return False
        last_sent = datetime.fromisoformat(row[0])
        return now - last_sent >= timedelta(days=7)
    finally:
        conn.close()


def mark_weekly_summary_sent(*, now: datetime | None = None) -> None:
    now = now or datetime.now(timezone.utc)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO system_meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            ("weekly_health_summary", now.isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
