"""Poll every registered company for new job postings and alert on new ones.

Run repeatedly (cron / launchd / a `while true; sleep` loop) — each run
fetches, filters (each company decides its own — see companies/README.md),
diffs against careers/jobs.db, and sends a text + email for anything
genuinely new. Add a company by dropping a new folder under companies/; it's
auto-discovered.

Fetching is concurrent, everything after it is not — see MAX_WORKERS.
"""

import time
from concurrent.futures import ThreadPoolExecutor

from . import db, notify
from .companies import COMPANIES

# Fetching is I/O-bound, so this is sized by memory, not by CPU. Each
# in-flight company holds a raw response plus its parsed form; only the
# four-string job dicts outlive the fetch. Measured over 100 companies
# against 2MB responses: 1 worker = 18.8s / 28MB peak heap, 12 workers =
# 1.8s / 33MB, 100 workers = 1.5s / 148MB. Past ~12 the wall clock stops
# improving (the pool is already deeper than the latency requires) while
# peak memory keeps climbing with response size — and a board fatter than
# 2MB scales that 148MB figure linearly, into OOM range on a 1GB box.
# Raise this only if you hit a real wall-clock wall, never for tidiness.
MAX_WORKERS = 12


def _fetch(company) -> list[dict]:
    """Fetch + filter one company. Runs on a pool thread; touches no shared state."""
    jobs = company.fetch_jobs()
    if hasattr(company, "filter_jobs"):
        jobs = company.filter_jobs(jobs)
    return jobs


def run() -> None:
    notify.ensure_opted_in()
    started = time.monotonic()

    # Fetch concurrently...
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_fetch, company): company for company in COMPANIES}
        results = {}
        failures = []
        for future, company in futures.items():
            try:
                results[company] = future.result()
            except Exception as exc:
                # One rotted persisted-query id or dead career site must not
                # take down the other 99 companies' polls.
                failures.append(company.COMPANY_NAME)
                print(f"[{company.COMPANY_NAME}] FETCH FAILED: {type(exc).__name__}: {exc}")

    # ...but diff and alert serially on the main thread. sqlite doesn't want
    # concurrent writers to one file, Twilio rate-limits, and both legs are
    # fast enough that there's nothing to win by parallelizing them.
    for company, jobs in results.items():
        new_jobs = db.sync_and_get_new(company.COMPANY_NAME, jobs)

        for job in new_jobs:
            print(f"[{company.COMPANY_NAME}] new: {job['title']} ({', '.join(job['locations'])})")
            notify.notify_new_job(company.COMPANY_NAME, job)

        if not new_jobs:
            print(f"[{company.COMPANY_NAME}] no new postings ({len(jobs)} match filters)")

    elapsed = time.monotonic() - started
    summary = f"polled {len(results)}/{len(COMPANIES)} companies in {elapsed:.1f}s"
    if failures:
        summary += f" — failed: {', '.join(failures)}"
    print(summary)


if __name__ == "__main__":
    run()
