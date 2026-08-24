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
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator
from urllib.parse import urlsplit

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

DB_PATH = Path(
    os.environ.get("JOB_POLLER_DB_PATH") or PROJECT_DIR / "jobs.db"
).expanduser()

_SQLITE_SCHEMA = """
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

_POSTGRES_CONNECTION = None
_POSTGRES_CONNECTION_URL = ""


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
    """Split the deliberately simple SQL migration files into statements."""
    return [statement.strip() for statement in contents.split(";") if statement.strip()]


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
    return conn


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


def sync_and_get_new(company: str, jobs: list[dict]) -> list[dict]:
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
        for job in jobs:
            _execute(
                conn,
                "INSERT INTO jobs (company, job_id, title, locations, first_seen) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(company, job_id) DO NOTHING",
                (company, job["id"], job["title"], ", ".join(job["locations"]), now),
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
