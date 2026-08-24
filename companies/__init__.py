"""Registry of every company watch.py polls.

Every folder under companies/ is auto-discovered and imported here — no
manual registration step. Each must expose:
    COMPANY_NAME: str
    fetch_jobs() -> list[dict]        # each dict: id, title, locations, url
    filter_jobs(jobs) -> list[dict]   # optional; omit for no filtering

There's no filter applied here on their behalf — every site's postings look
different, so filtering is each company's own call (reuse filters.py's
predicates, or write your own). See README.md for a walkthrough.
"""

import importlib
import os
import pkgutil
from pathlib import Path

from dotenv import load_dotenv

from ..profiles import (
    AEROSPACE_TARGET_COMPANIES,
    normalized_profile,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_disabled = {
    name.strip().lower()
    for name in os.environ.get("JOB_POLLER_DISABLED_COMPANIES", "").split(",")
    if name.strip()
}

_profile = normalized_profile(os.environ.get("JOB_POLLER_PROFILE"))
_allowlisted = {
    name.strip().lower()
    for name in os.environ.get("JOB_POLLER_COMPANIES", "").split(",")
    if name.strip()
}

COMPANIES = []
for _module_info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
    if not _module_info.ispkg:
        continue
    if _module_info.name.lower() in _disabled:
        continue
    _module = importlib.import_module(f"{__name__}.{_module_info.name}")
    assert hasattr(_module, "COMPANY_NAME"), f"companies/{_module_info.name}: missing COMPANY_NAME"
    assert hasattr(_module, "fetch_jobs"), f"companies/{_module_info.name}: missing fetch_jobs()"
    if _profile == "aerospace" and _module.COMPANY_NAME not in AEROSPACE_TARGET_COMPANIES:
        continue
    if _allowlisted and not (
        _module_info.name.lower() in _allowlisted
        or _module.COMPANY_NAME.lower() in _allowlisted
    ):
        continue
    COMPANIES.append(_module)
