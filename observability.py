"""Small, safe, per-company JSONL audit logs for polling runs.

These files complement (rather than replace) the concise stdout messages that
systemd stores in journald.  Keep request payloads, response bodies, cookies,
and authorization headers out of these logs: career sites routinely put
short-lived credentials in them.
"""

from __future__ import annotations

import contextvars
import json
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


LOG_DIR = Path(__file__).resolve().parent / "logs"
MAX_LOG_BYTES = 1_000_000
LOG_BACKUPS = 3
_company: contextvars.ContextVar[str | None] = contextvars.ContextVar("log_company", default=None)
_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("log_run_id", default=None)
_write_lock = threading.Lock()


def set_context(company: str, run_id: str):
    """Attach company/run identifiers to events produced by the current thread."""
    return _company.set(company), _run_id.set(run_id)


def reset_context(tokens) -> None:
    company_token, run_token = tokens
    _company.reset(company_token)
    _run_id.reset(run_token)


def current_company() -> str | None:
    return _company.get()


def _rotate(path: Path) -> None:
    """Keep the active file plus a small number of numbered history files."""
    if not path.exists() or path.stat().st_size < MAX_LOG_BYTES:
        return
    oldest = path.with_suffix(path.suffix + f".{LOG_BACKUPS}")
    oldest.unlink(missing_ok=True)
    for number in range(LOG_BACKUPS - 1, 0, -1):
        previous = path.with_suffix(path.suffix + f".{number}")
        if previous.exists():
            previous.replace(path.with_suffix(path.suffix + f".{number + 1}"))
    path.replace(path.with_suffix(path.suffix + ".1"))


def log_event(company: str | None = None, event: str = "event", **fields: Any) -> None:
    """Append one structured event to ``logs/<company>.jsonl``.

    A small global lock keeps a line intact should two poller processes ever
    overlap.  Files are intentionally plain JSON Lines so they can be tailed,
    grepped, or loaded into a log tool without another dependency.
    """
    company = company or _company.get()
    if not company:
        return
    safe_name = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-") or "unknown"
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "run_id": _run_id.get(),
        "company": company,
        "event": event,
        **fields,
    }
    try:
        LOG_DIR.mkdir(mode=0o750, exist_ok=True)
        path = LOG_DIR / f"{safe_name}.jsonl"
        with _write_lock:
            _rotate(path)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, separators=(",", ":"), default=str) + "\n")
    except OSError:
        # Logging must never make a job-board poll fail.
        pass
