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
import pkgutil

COMPANIES = []
for _module_info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
    if not _module_info.ispkg:
        continue
    _module = importlib.import_module(f"{__name__}.{_module_info.name}")
    assert hasattr(_module, "COMPANY_NAME"), f"companies/{_module_info.name}: missing COMPANY_NAME"
    assert hasattr(_module, "fetch_jobs"), f"companies/{_module_info.name}: missing fetch_jobs()"
    COMPANIES.append(_module)
