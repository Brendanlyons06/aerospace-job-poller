"""Durable job-poller state with local SQLite and cloud PostgreSQL backends.

Local development keeps the zero-configuration SQLite behavior. Cloud runs
set ``JOB_POLLER_DATABASE_URL`` to a Supabase PostgreSQL connection string.
The public functions intentionally stay backend-neutral so deduplication,
notification retries, source health, and weekly summaries behave identically
in both environments.
"""

from __future__ import annotations

import atexit
import json
import os
import sqlite3
import re
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from .job_metadata import company_sector, enrich_job


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

PACIFIC_TIME = ZoneInfo("America/Los_Angeles")

DB_PATH = Path(
    os.environ.get("JOB_POLLER_DB_PATH") or PROJECT_DIR / "jobs.db"
).expanduser()

_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    title TEXT NOT NULL,
    locations TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    sector TEXT,
    discipline TEXT,
    employment_type TEXT,
    work_mode TEXT,
    posted_at TEXT,
    closes_at TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT,
    closed_at TEXT,
    missed_polls INTEGER NOT NULL DEFAULT 0,
    compensation_min REAL,
    compensation_max REAL,
    compensation_currency TEXT,
    compensation_period TEXT,
    PRIMARY KEY (company, job_id)
);

CREATE TABLE IF NOT EXISTS companies (
    company TEXT PRIMARY KEY,
    slug TEXT,
    sector TEXT NOT NULL,
    careers_url TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_locations (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    location_index INTEGER NOT NULL,
    label TEXT NOT NULL,
    city TEXT,
    state TEXT,
    country TEXT,
    latitude REAL,
    longitude REAL,
    PRIMARY KEY (company, job_id, location_index)
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

CREATE TABLE IF NOT EXISTS email_subscriptions (
    email TEXT PRIMARY KEY,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly')),
    discipline TEXT,
    sector TEXT,
    company TEXT,
    state TEXT,
    states TEXT,
    verification_token TEXT NOT NULL,
    unsubscribe_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    verification_requested_at TEXT NOT NULL,
    verification_sent_at TEXT,
    manage_requested_at TEXT,
    manage_sent_at TEXT,
    confirmed_at TEXT,
    unsubscribed_at TEXT,
    last_digest_at TEXT,
    next_digest_at TEXT,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    last_error TEXT
);
"""

_POSTGRES_CONNECTION = None
_POSTGRES_CONNECTION_URL = ""

_SQLITE_JOB_COLUMNS = {
    "url": "TEXT NOT NULL DEFAULT ''",
    "sector": "TEXT",
    "discipline": "TEXT",
    "employment_type": "TEXT",
    "work_mode": "TEXT",
    "posted_at": "TEXT",
    "closes_at": "TEXT",
    "last_seen": "TEXT",
    "closed_at": "TEXT",
    "missed_polls": "INTEGER NOT NULL DEFAULT 0",
    "compensation_min": "REAL",
    "compensation_max": "REAL",
    "compensation_currency": "TEXT",
    "compensation_period": "TEXT",
}

_SQLITE_SUBSCRIPTION_COLUMNS = {
    "states": "TEXT",
    "manage_requested_at": "TEXT",
    "manage_sent_at": "TEXT",
}


def _database_url() -> str:
    """Return the poller-specific database URL without accepting generic URLs."""
    return os.environ.get("JOB_POLLER_DATABASE_URL", "").strip()


def _postgres_required() -> bool:
    return os.environ.get("JOB_POLLER_REQUIRE_POSTGRES", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def backend_name() -> str:
    """Describe the active persistence backend without exposing credentials."""
    return "postgresql" if _database_url() else "sqlite"


def _validate_database_url_shape(database_url: str) -> None:
    """Catch common Supabase copy/paste mistakes without exposing the URL."""
    if "[YOUR-PASSWORD]" in database_url:
        raise RuntimeError(
            "Replace [YOUR-PASSWORD] in the Supabase connection string"
        )
    try:
        parsed = urlsplit(database_url)
        port = parsed.port
    except ValueError as exc:
        raise RuntimeError(
            "The Supabase connection string is malformed; recopy it from Connect"
        ) from exc
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("The database secret must be a PostgreSQL connection string")
    if parsed.hostname and parsed.hostname.endswith(".pooler.supabase.com"):
        if not (parsed.username or "").startswith("postgres."):
            raise RuntimeError(
                "The Supabase shared-pooler username must be "
                "postgres.<project-reference>; recopy the Transaction pooler URI"
            )
        if port != 6543:
            raise RuntimeError(
                "The Supabase Transaction pooler URI must use port 6543"
            )


def _migration_statements(contents: str) -> list[str]:
    """Split SQL while preserving quoted strings and dollar-quoted functions."""
    statements = []
    start = 0
    index = 0
    quote = None
    dollar_tag = None
    while index < len(contents):
        if dollar_tag:
            if contents.startswith(dollar_tag, index):
                index += len(dollar_tag)
                dollar_tag = None
            else:
                index += 1
            continue
        character = contents[index]
        if quote:
            if character == quote:
                if index + 1 < len(contents) and contents[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if contents.startswith("--", index):
            newline = contents.find("\n", index + 2)
            index = len(contents) if newline < 0 else newline + 1
            continue
        if contents.startswith("/*", index):
            close = contents.find("*/", index + 2)
            index = len(contents) if close < 0 else close + 2
            continue
        if character in {"'", '"'}:
            quote = character
            index += 1
            continue
        if character == "$":
            match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", contents[index:])
            if match:
                dollar_tag = match.group(0)
                index += len(dollar_tag)
                continue
        if character == ";":
            statement = contents[start:index].strip()
            if statement:
                statements.append(statement)
            start = index + 1
        index += 1
    tail = contents[start:].strip()
    if tail:
        statements.append(tail)
    return statements


def _apply_postgres_migrations(conn) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
    )
    conn.commit()
    applied = {
        row[0]
        for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
    }
    migration_dir = PROJECT_DIR / "supabase" / "migrations"
    for migration_path in sorted(migration_dir.glob("[0-9]*.sql")):
        version = migration_path.name
        if version in applied:
            continue
        try:
            for statement in _migration_statements(migration_path.read_text()):
                conn.execute(statement)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)", (version,)
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def _close_postgres_connection() -> None:
    global _POSTGRES_CONNECTION
    if _POSTGRES_CONNECTION is not None and not _POSTGRES_CONNECTION.closed:
        _POSTGRES_CONNECTION.close()
    _POSTGRES_CONNECTION = None


atexit.register(_close_postgres_connection)


def _postgres_connect():
    """Open one reusable connection for the short-lived poller process."""
    global _POSTGRES_CONNECTION, _POSTGRES_CONNECTION_URL
    database_url = _database_url()
    if not database_url:
        raise RuntimeError("JOB_POLLER_DATABASE_URL is not configured")
    _validate_database_url_shape(database_url)

    if (
        _POSTGRES_CONNECTION is not None
        and not _POSTGRES_CONNECTION.closed
        and _POSTGRES_CONNECTION_URL == database_url
    ):
        return _POSTGRES_CONNECTION

    _close_postgres_connection()
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - only possible in a bad deployment
        raise RuntimeError(
            "PostgreSQL support is missing; install the packages in requirements.txt"
        ) from exc

    # Supabase's transaction pooler does not support named prepared statements.
    # Keeping preparation disabled also makes this work with direct/session URLs.
    _POSTGRES_CONNECTION = psycopg.connect(
        database_url,
        connect_timeout=15,
        prepare_threshold=None,
        application_name="aerospace-job-poller",
        sslmode="require",
    )
    _POSTGRES_CONNECTION_URL = database_url
    _apply_postgres_migrations(_POSTGRES_CONNECTION)
    return _POSTGRES_CONNECTION


def _connect():
    """Connect to the configured backend; kept public for local diagnostics."""
    if _database_url():
        return _postgres_connect()
    if _postgres_required():
        raise RuntimeError(
            "Cloud mode requires the JOB_POLLER_DATABASE_URL GitHub secret"
        )
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SQLITE_SCHEMA)
    _upgrade_sqlite_schema(conn)
    return conn


def _upgrade_sqlite_schema(conn: sqlite3.Connection) -> None:
    """Add Phase 2 columns to an existing local database without data loss."""
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
    }
    for name, definition in _SQLITE_JOB_COLUMNS.items():
        if name not in columns:
            conn.execute(f"ALTER TABLE jobs ADD COLUMN {name} {definition}")
    conn.execute("UPDATE jobs SET last_seen = first_seen WHERE last_seen IS NULL")
    subscription_columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(email_subscriptions)").fetchall()
    }
    for name, definition in _SQLITE_SUBSCRIPTION_COLUMNS.items():
        if name not in subscription_columns:
            conn.execute(
                f"ALTER TABLE email_subscriptions ADD COLUMN {name} {definition}"
            )
    conn.execute(
        "UPDATE email_subscriptions SET states = UPPER(state) "
        "WHERE states IS NULL AND state IS NOT NULL"
    )
    conn.commit()


def _execute(conn, statement: str, parameters: tuple = ()):
    """Execute portable SQL, translating only the parameter marker syntax."""
    if isinstance(conn, sqlite3.Connection):
        return conn.execute(statement, parameters)
    return conn.execute(statement.replace("?", "%s"), parameters)


@contextmanager
def _connection() -> Iterator:
    conn = _connect()
    try:
        yield conn
        # End read-only transactions too. This is especially important for a
        # transaction-pooler connection, which returns its server connection
        # to the shared pool only at the transaction boundary.
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        # The cloud process reuses one TLS connection for the whole poll. Local
        # SQLite connections remain short-lived exactly as before.
        if isinstance(conn, sqlite3.Connection):
            conn.close()


def validate_configuration() -> str:
    """Fail before polling when cloud persistence is missing or unreachable."""
    backend = backend_name()
    if _postgres_required() and backend != "postgresql":
        raise RuntimeError(
            "Cloud mode requires the JOB_POLLER_DATABASE_URL GitHub secret"
        )
    if backend == "postgresql":
        with _connection() as conn:
            _execute(conn, "SELECT 1").fetchone()
    return backend


def sync_and_get_new(
    company: str,
    jobs: list[dict],
    *,
    company_slug: str | None = None,
    careers_url: str | None = None,
) -> list[dict]:
    """Record jobs and return every undelivered alert for this company.

    On a company's first-ever sync, seeds all current jobs as seen and
    returns [] (bootstrap — nothing to alert on yet). After initialization,
    newly discovered jobs enter a durable outbox. A failed email therefore
    remains pending and is retried on a later poll instead of being lost.
    """
    with _connection() as conn:
        already_initialized = _execute(
            conn, "SELECT 1 FROM companies_meta WHERE company = ?", (company,)
        ).fetchone() is not None

        existing_ids = {
            row[0]
            for row in _execute(
                conn, "SELECT job_id FROM jobs WHERE company = ?", (company,)
            )
        }

        now = datetime.now(timezone.utc).isoformat()
        sector = company_sector(company)
        _execute(
            conn,
            "INSERT INTO companies "
            "(company, slug, sector, careers_url, first_seen, last_seen) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(company) DO UPDATE SET "
            "slug = COALESCE(excluded.slug, companies.slug), "
            "sector = excluded.sector, "
            "careers_url = COALESCE(excluded.careers_url, companies.careers_url), "
            "last_seen = excluded.last_seen",
            (company, company_slug, sector, careers_url, now, now),
        )

        current_ids = [job["id"] for job in jobs]
        if current_ids:
            placeholders = ", ".join("?" for _ in current_ids)
            _execute(
                conn,
                "UPDATE jobs SET missed_polls = missed_polls + 1 "
                "WHERE company = ? AND closed_at IS NULL "
                f"AND job_id NOT IN ({placeholders})",
                (company, *current_ids),
            )
        else:
            _execute(
                conn,
                "UPDATE jobs SET missed_polls = missed_polls + 1 "
                "WHERE company = ? AND closed_at IS NULL",
                (company,),
            )

        for job in jobs:
            metadata = enrich_job(company, job)
            _execute(
                conn,
                "INSERT INTO jobs "
                "(company, job_id, title, locations, url, sector, discipline, "
                "employment_type, work_mode, posted_at, closes_at, first_seen, "
                "last_seen, closed_at, missed_polls, compensation_min, "
                "compensation_max, compensation_currency, compensation_period) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 0, ?, ?, ?, ?) "
                "ON CONFLICT(company, job_id) DO UPDATE SET "
                "title = excluded.title, locations = excluded.locations, "
                "url = excluded.url, sector = excluded.sector, "
                "discipline = excluded.discipline, "
                "employment_type = COALESCE(excluded.employment_type, jobs.employment_type), "
                "work_mode = COALESCE(excluded.work_mode, jobs.work_mode), "
                "posted_at = COALESCE(excluded.posted_at, jobs.posted_at), "
                "closes_at = COALESCE(excluded.closes_at, jobs.closes_at), "
                "last_seen = excluded.last_seen, closed_at = NULL, missed_polls = 0, "
                "compensation_min = COALESCE(excluded.compensation_min, jobs.compensation_min), "
                "compensation_max = COALESCE(excluded.compensation_max, jobs.compensation_max), "
                "compensation_currency = COALESCE(excluded.compensation_currency, jobs.compensation_currency), "
                "compensation_period = COALESCE(excluded.compensation_period, jobs.compensation_period)",
                (
                    company,
                    job["id"],
                    job["title"],
                    ", ".join(job["locations"]),
                    job.get("url", ""),
                    metadata["sector"],
                    metadata["discipline"],
                    metadata["employment_type"],
                    metadata["work_mode"],
                    metadata["posted_at"],
                    metadata["closes_at"],
                    now,
                    now,
                    metadata["compensation_min"],
                    metadata["compensation_max"],
                    metadata["compensation_currency"],
                    metadata["compensation_period"],
                ),
            )
            _execute(
                conn,
                "DELETE FROM job_locations WHERE company = ? AND job_id = ?",
                (company, job["id"]),
            )
            for index, location in enumerate(metadata["structured_locations"]):
                _execute(
                    conn,
                    "INSERT INTO job_locations "
                    "(company, job_id, location_index, label, city, state, country, "
                    "latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        company,
                        job["id"],
                        index,
                        location["label"],
                        location["city"],
                        location["state"],
                        location["country"],
                        location["latitude"],
                        location["longitude"],
                    ),
                )

        _execute(
            conn,
            "UPDATE jobs SET closed_at = ?, missed_polls = 2 "
            "WHERE company = ? AND closed_at IS NULL AND missed_polls >= 2",
            (now, company),
        )

        if not already_initialized:
            _execute(
                conn,
                "INSERT INTO companies_meta (company, initialized_at) VALUES (?, ?) "
                "ON CONFLICT(company) DO NOTHING",
                (company, now),
            )
            conn.commit()
            return []

        for job in jobs:
            if job["id"] in existing_ids:
                continue
            _execute(
                conn,
                "INSERT INTO notification_outbox "
                "(company, job_id, title, locations, url, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(company, job_id) DO NOTHING",
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
        rows = _execute(
            conn,
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


def mark_notification_delivered(company: str, job_id: str) -> None:
    """Mark an outbox item delivered so later polls do not resend it."""
    with _connection() as conn:
        _execute(
            conn,
            "UPDATE notification_outbox SET delivered_at = ?, last_error = NULL "
            "WHERE company = ? AND job_id = ?",
            (datetime.now(timezone.utc).isoformat(), company, job_id),
        )
        conn.commit()


def mark_notification_failed(company: str, job_id: str, error: str) -> None:
    """Record a failed attempt while leaving the outbox item pending."""
    with _connection() as conn:
        _execute(
            conn,
            "UPDATE notification_outbox "
            "SET attempts = attempts + 1, last_error = ? "
            "WHERE company = ? AND job_id = ?",
            (error[:1000], company, job_id),
        )
        conn.commit()


def record_poll_failure(company: str, error: str) -> tuple[int, bool]:
    """Record a board failure and say whether it just reached alert threshold."""
    with _connection() as conn:
        row = _execute(
            conn,
            "SELECT consecutive_failures FROM company_health WHERE company = ?",
            (company,),
        ).fetchone()
        count = (row[0] if row else 0) + 1
        _execute(
            conn,
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


def record_poll_success(company: str, job_count: int) -> tuple[bool, int]:
    """Record a successful board poll and return (recovered, zero streak)."""
    with _connection() as conn:
        row = _execute(
            conn,
            "SELECT consecutive_failures, consecutive_zero "
            "FROM company_health WHERE company = ?",
            (company,),
        ).fetchone()
        previous_failures, previous_zero = row or (0, 0)
        zero_count = previous_zero + 1 if job_count == 0 else 0
        _execute(
            conn,
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


def health_snapshot() -> list[dict]:
    """Return company health rows for summaries and diagnostics."""
    with _connection() as conn:
        rows = _execute(
            conn,
            "SELECT company, consecutive_failures, consecutive_zero, last_success, "
            "last_failure, last_error, last_job_count "
            "FROM company_health ORDER BY company",
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


def weekly_summary_due(*, now: datetime | None = None) -> bool:
    """Return true weekly, establishing a baseline without an immediate email."""
    now = now or datetime.now(timezone.utc)
    with _connection() as conn:
        row = _execute(
            conn, "SELECT value FROM system_meta WHERE key = 'weekly_health_summary'"
        ).fetchone()
        if not row:
            _execute(
                conn,
                "INSERT INTO system_meta (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO NOTHING",
                ("weekly_health_summary", now.isoformat()),
            )
            conn.commit()
            return False
        last_sent = datetime.fromisoformat(row[0])
        return now - last_sent >= timedelta(days=7)


def mark_weekly_summary_sent(*, now: datetime | None = None) -> None:
    now = now or datetime.now(timezone.utc)
    with _connection() as conn:
        _execute(
            conn,
            "INSERT INTO system_meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            ("weekly_health_summary", now.isoformat()),
        )
        conn.commit()


def mark_poll_completed(*, now: datetime | None = None) -> None:
    """Record when a full poll completed for dashboard freshness display."""
    now = now or datetime.now(timezone.utc)
    with _connection() as conn:
        _execute(
            conn,
            "INSERT INTO system_meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            ("last_poll_completed_at", now.isoformat()),
        )
        conn.commit()


def pending_subscription_verifications(*, limit: int = 10) -> list[dict]:
    """Return pending confirmations that have not yet received an email."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    with _connection() as conn:
        rows = _execute(
            conn,
            "SELECT email, verification_token, unsubscribe_token, frequency, discipline, sector, "
            "company, state FROM email_subscriptions "
            "WHERE confirmed_at IS NULL AND unsubscribed_at IS NULL "
            "AND verification_sent_at IS NULL AND verification_requested_at >= ? "
            "ORDER BY verification_requested_at LIMIT ?",
            (cutoff, max(1, min(limit, 25))),
        ).fetchall()
    return [
        {
            "email": row[0],
            "verification_token": row[1],
            "unsubscribe_token": row[2],
            "frequency": row[3],
            "discipline": row[4],
            "sector": row[5],
            "company": row[6],
            "state": row[7],
        }
        for row in rows
    ]


def cleanup_expired_subscription_requests(*, now: datetime | None = None) -> int:
    """Delete unconfirmed requests once their seven-day link is long expired."""
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=30)).isoformat()
    with _connection() as conn:
        cursor = _execute(
            conn,
            "DELETE FROM email_subscriptions WHERE confirmed_at IS NULL "
            "AND created_at < ?",
            (cutoff,),
        )
        conn.commit()
        return max(0, cursor.rowcount)


def mark_subscription_verification_sent(
    email: str, *, now: datetime | None = None
) -> None:
    now = now or datetime.now(timezone.utc)
    with _connection() as conn:
        _execute(
            conn,
            "UPDATE email_subscriptions SET verification_sent_at = ?, last_error = NULL "
            "WHERE email = ? AND confirmed_at IS NULL",
            (now.isoformat(), email),
        )
        conn.commit()


def pending_subscription_management_emails(*, limit: int = 10) -> list[dict]:
    """Return verified subscribers waiting for a fresh private management link."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    with _connection() as conn:
        rows = _execute(
            conn,
            "SELECT email, unsubscribe_token FROM email_subscriptions "
            "WHERE confirmed_at IS NOT NULL AND unsubscribed_at IS NULL "
            "AND manage_requested_at IS NOT NULL AND manage_sent_at IS NULL "
            "AND manage_requested_at >= ? ORDER BY manage_requested_at LIMIT ?",
            (cutoff, max(1, min(limit, 25))),
        ).fetchall()
    return [{"email": row[0], "manage_token": row[1]} for row in rows]


def mark_subscription_management_sent(
    email: str, *, now: datetime | None = None
) -> None:
    now = now or datetime.now(timezone.utc)
    with _connection() as conn:
        _execute(
            conn,
            "UPDATE email_subscriptions SET manage_sent_at = ?, last_error = NULL "
            "WHERE email = ? AND confirmed_at IS NOT NULL AND unsubscribed_at IS NULL",
            (now.isoformat(), email),
        )
        conn.commit()


def mark_subscription_delivery_failed(email: str, error: str) -> None:
    """Record a delivery failure without exposing it through the dashboard."""
    with _connection() as conn:
        _execute(
            conn,
            "UPDATE email_subscriptions SET consecutive_failures = "
            "consecutive_failures + 1, last_error = ? WHERE email = ?",
            (error[:1000], email),
        )
        conn.commit()


def public_email_send_available(
    *, now: datetime | None = None, daily_cap: int = 200
) -> bool:
    """Keep public delivery below a conservative daily Gmail allowance."""
    now = now or datetime.now(timezone.utc)
    key = f"public_email_sent_{now.date().isoformat()}"
    with _connection() as conn:
        row = _execute(
            conn, "SELECT value FROM system_meta WHERE key = ?", (key,)
        ).fetchone()
        return int(row[0]) < daily_cap if row else True


def record_public_email_sent(*, now: datetime | None = None) -> None:
    now = now or datetime.now(timezone.utc)
    key = f"public_email_sent_{now.date().isoformat()}"
    with _connection() as conn:
        _execute(
            conn,
            "INSERT INTO system_meta (key, value) VALUES (?, '1') "
            "ON CONFLICT(key) DO UPDATE SET value = "
            "CAST(CAST(system_meta.value AS INTEGER) + 1 AS TEXT)",
            (key,),
        )
        conn.commit()


def subscription_summary(*, now: datetime | None = None) -> dict[str, int]:
    """Return private aggregate subscription metrics for the owner report."""
    now = now or datetime.now(timezone.utc)
    daily_key = f"public_email_sent_{now.date().isoformat()}"
    with _connection() as conn:
        row = _execute(
            conn,
            "SELECT "
            "SUM(CASE WHEN confirmed_at IS NOT NULL AND unsubscribed_at IS NULL THEN 1 ELSE 0 END), "
            "SUM(CASE WHEN confirmed_at IS NULL AND unsubscribed_at IS NULL THEN 1 ELSE 0 END), "
            "SUM(CASE WHEN unsubscribed_at IS NOT NULL THEN 1 ELSE 0 END), "
            "SUM(CASE WHEN consecutive_failures > 0 THEN 1 ELSE 0 END) "
            "FROM email_subscriptions",
        ).fetchone()
        sent_row = _execute(
            conn, "SELECT value FROM system_meta WHERE key = ?", (daily_key,)
        ).fetchone()
    return {
        "active": int(row[0] or 0),
        "pending": int(row[1] or 0),
        "unsubscribed": int(row[2] or 0),
        "delivery_failures": int(row[3] or 0),
        "emails_sent_today": int(sent_row[0]) if sent_row else 0,
        "subscriber_cap": 100,
        "daily_email_cap": 200,
    }


def due_subscription_digests(
    *, now: datetime | None = None, limit: int = 20
) -> list[dict]:
    """Return due subscribers with matching jobs discovered since their last digest."""
    now = now or datetime.now(timezone.utc)
    with _connection() as conn:
        subscriptions = _execute(
            conn,
            "SELECT email, frequency, discipline, sector, company, state, states, "
            "unsubscribe_token, COALESCE(last_digest_at, confirmed_at) "
            "FROM email_subscriptions WHERE confirmed_at IS NOT NULL "
            "AND unsubscribed_at IS NULL AND next_digest_at <= ? "
            "ORDER BY next_digest_at, email LIMIT ?",
            (now.isoformat(), max(1, min(limit, 100))),
        ).fetchall()

        digests = []
        for subscription in subscriptions:
            email, frequency, discipline, sector, company, state, states, token, cutoff = subscription
            conditions = ["j.closed_at IS NULL", "j.first_seen > ?"]
            parameters: list[object] = [cutoff]
            if discipline:
                conditions.append("j.discipline = ?")
                parameters.append(discipline)
            if sector:
                conditions.append("j.sector = ?")
                parameters.append(sector)
            if company:
                conditions.append("j.company = ?")
                parameters.append(company)
            selected_states = [
                value.strip().upper()
                for value in (states or state or "").split(",")
                if value.strip()
            ]
            geographic_states = [value for value in selected_states if value != "REMOTE"]
            location_filters = []
            if geographic_states:
                placeholders = ", ".join("?" for _ in geographic_states)
                location_filters.append(
                    "EXISTS (SELECT 1 FROM job_locations AS jl "
                    "WHERE jl.company = j.company AND jl.job_id = j.job_id "
                    f"AND UPPER(jl.state) IN ({placeholders}))"
                )
                parameters.extend(geographic_states)
            if "REMOTE" in selected_states:
                location_filters.append("j.work_mode = 'remote'")
            if location_filters:
                conditions.append("(" + " OR ".join(location_filters) + ")")
            rows = _execute(
                conn,
                "SELECT j.company, j.title, j.locations, j.url, j.first_seen "
                "FROM jobs AS j WHERE " + " AND ".join(conditions) +
                " ORDER BY j.first_seen DESC LIMIT 25",
                tuple(parameters),
            ).fetchall()
            digests.append(
                {
                    "email": email,
                    "frequency": frequency,
                    "unsubscribe_token": token,
                    "jobs": [
                        {
                            "company": row[0],
                            "title": row[1],
                            "locations": row[2],
                            "url": row[3],
                            "first_seen": row[4],
                        }
                        for row in rows
                    ],
                }
            )
        return digests


def _next_digest_time(frequency: str, now: datetime) -> datetime:
    """Return the next 9:00 AM Pacific digest boundary in UTC."""
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    local_now = now.astimezone(PACIFIC_TIME)
    days_ahead = (7 - local_now.weekday()) if frequency == "weekly" else 1
    local_next = (local_now + timedelta(days=days_ahead)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    return local_next.astimezone(timezone.utc)


def mark_subscription_digest_complete(
    email: str, frequency: str, *, now: datetime | None = None
) -> None:
    """Advance a digest whether or not it contained new matching jobs."""
    now = now or datetime.now(timezone.utc)
    next_digest = _next_digest_time(frequency, now)
    with _connection() as conn:
        _execute(
            conn,
            "UPDATE email_subscriptions SET last_digest_at = ?, next_digest_at = ?, "
            "consecutive_failures = 0, last_error = NULL WHERE email = ? "
            "AND unsubscribed_at IS NULL",
            (now.isoformat(), next_digest.isoformat(), email),
        )
        conn.commit()
