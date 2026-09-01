"""Run a recovery poll only when the primary schedule has fallen behind."""

from __future__ import annotations

import os
from datetime import timedelta

from . import db, watch


def _stale_after_minutes() -> int:
    raw = os.environ.get("JOB_POLLER_STALE_AFTER_MINUTES", "120").strip()
    try:
        return max(30, int(raw))
    except ValueError as exc:
        raise RuntimeError("JOB_POLLER_STALE_AFTER_MINUTES must be an integer") from exc


def run() -> None:
    backend = db.validate_configuration()
    threshold = _stale_after_minutes()
    print(f"database backend: {backend}")
    if not db.poll_is_stale(max_age=timedelta(minutes=threshold)):
        print(f"latest poll is under {threshold} minutes old; recovery poll not needed")
        return
    print(f"latest poll is missing or over {threshold} minutes old; starting recovery poll")
    watch.run()


if __name__ == "__main__":
    run()
