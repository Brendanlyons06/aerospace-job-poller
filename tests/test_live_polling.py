"""Live, read-only verification of every company adapter.

Run explicitly when changing an adapter or before deploying:

    RUN_LIVE_POLL_TESTS=1 python3 -m unittest discover -s tests -v

The test makes only public, read-only requests.  It neither opens jobs.db nor
sends notifications.  Empty results are permitted because internship hiring
is seasonal; a successful empty response is still the current list.
"""

from __future__ import annotations

import importlib
import os
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PARENT = PROJECT_ROOT.parent
sys.path[:] = [
    entry for entry in sys.path
    if Path(entry or ".").resolve() != PROJECT_ROOT
]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

PACKAGE = "Job-poller"
check = importlib.import_module(f"{PACKAGE}.check")
companies_module = importlib.import_module(f"{PACKAGE}.companies")
filters = importlib.import_module(f"{PACKAGE}.filters")


def poll(company):
    jobs = company.fetch_jobs()
    filtered = company.filter_jobs(jobs) if hasattr(company, "filter_jobs") else jobs
    return company, jobs, filtered


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_POLL_TESTS") == "1",
    "live job-board requests are opt-in; set RUN_LIVE_POLL_TESTS=1",
)
class LivePollingTests(unittest.TestCase):
    def test_every_adapter_returns_a_current_valid_internship_list(self) -> None:
        failures = []
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {
                pool.submit(poll, company): company
                for company in companies_module.COMPANIES
            }
            for future in as_completed(futures):
                company = futures[future]
                try:
                    company, jobs, filtered = future.result()
                    errors = check._validate(jobs, "fetch_jobs()")
                    errors += check._validate(filtered, "filter_jobs()")
                    source_ids = {item["id"] for item in jobs if isinstance(item, dict) and "id" in item}
                    filtered_ids = {item["id"] for item in filtered if isinstance(item, dict) and "id" in item}
                    if not filtered_ids.issubset(source_ids):
                        errors.append("filter_jobs() returned a posting that was not fetched")
                    non_us = [
                        item["title"] for item in filtered
                        if item.get("locations") and not filters.is_us_job(item)
                    ]
                    if non_us:
                        errors.append(f"non-US locations after filtering: {non_us[:3]}")
                    if errors:
                        failures.append(f"{company.COMPANY_NAME}: {'; '.join(errors)}")
                except Exception as exc:
                    failures.append(f"{company.COMPANY_NAME}: {type(exc).__name__}: {exc}")
        self.assertFalse(failures, "\n".join(failures))
