"""Validate company adapters without touching jobs.db or sending anything.

    python -m careers.check              # every company
    python -m careers.check anthropic    # one, by folder name or COMPANY_NAME
    python -m careers.check anthropic --twice

This is the thing to run after writing a new adapter. `watch.py` is a bad
test harness for one: it writes to jobs.db (so a company's one free
bootstrap run gets silently consumed by a broken adapter, and the real first
alert never fires) and it can send live texts. This runs fetch_jobs() and
filter_jobs() in isolation, checks the output against the contract in
companies/README.md, and prints what you'd have alerted on.

`--twice` fetches each board a second time and diffs the id sets. That's the
check for the mistake AGENTS.md warns about — ids derived from list position
or from mutable fields look perfectly fine in a single run and then report
the entire board as new on every poll forever.

Exits nonzero if any company fails, so it can gate a commit.
"""

import sys
import time

from .companies import COMPANIES

REQUIRED = {"id": str, "title": str, "locations": list, "url": str}


def _module_name(company) -> str:
    return company.__name__.rsplit(".", 1)[-1]


def _validate(jobs, label: str) -> list[str]:
    """Return a list of contract violations in a fetch_jobs()/filter_jobs() result."""
    errors = []
    if not isinstance(jobs, list):
        return [f"{label} returned {type(jobs).__name__}, expected list"]

    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            errors.append(f"{label}[{i}] is {type(job).__name__}, expected dict")
            continue
        for key, expected in REQUIRED.items():
            if key not in job:
                errors.append(f"{label}[{i}] missing {key!r}")
            elif not isinstance(job[key], expected):
                errors.append(
                    f"{label}[{i}][{key!r}] is {type(job[key]).__name__}, "
                    f"expected {expected.__name__}"
                )
        if isinstance(job.get("locations"), list) and not all(
            isinstance(loc, str) for loc in job["locations"]
        ):
            errors.append(f"{label}[{i}]['locations'] must be a list of str")
        if isinstance(job.get("id"), str) and not job["id"].strip():
            errors.append(f"{label}[{i}]['id'] is empty — it's the dedup key")
        if isinstance(job.get("url"), str) and not job["url"].startswith("http"):
            errors.append(f"{label}[{i}]['url'] is not a URL: {job['url']!r}")

    ids = [job["id"] for job in jobs if isinstance(job, dict) and isinstance(job.get("id"), str)]
    duplicates = len(ids) - len(set(ids))
    if duplicates:
        errors.append(f"{label}: {duplicates} duplicate id(s) — dedup will drop real postings")
    # Position-derived ids: every poll reshuffles them and every job looks new.
    if ids and set(ids) in ({str(i) for i in range(len(ids))}, {str(i + 1) for i in range(len(ids))}):
        errors.append(f"{label}: ids look like list indices, not stable posting ids")

    return errors


def check(company, twice: bool = False) -> bool:
    name = f"{company.COMPANY_NAME} ({_module_name(company)})"
    started = time.monotonic()
    try:
        jobs = company.fetch_jobs()
    except Exception as exc:
        print(f"FAIL {name}: fetch_jobs() raised {type(exc).__name__}: {exc}")
        return False
    elapsed = time.monotonic() - started

    errors = _validate(jobs, "fetch_jobs()")

    filtered = jobs
    if hasattr(company, "filter_jobs"):
        try:
            filtered = company.filter_jobs(jobs)
        except Exception as exc:
            print(f"FAIL {name}: filter_jobs() raised {type(exc).__name__}: {exc}")
            return False
        errors += _validate(filtered, "filter_jobs()")
        if isinstance(filtered, list) and len(filtered) > len(jobs):
            errors.append("filter_jobs() returned more jobs than it was given")

    if twice and not errors:
        try:
            again = {job["id"] for job in company.fetch_jobs()}
        except Exception as exc:
            print(f"FAIL {name}: second fetch_jobs() raised {type(exc).__name__}: {exc}")
            return False
        unstable = {job["id"] for job in jobs} ^ again
        if unstable:
            errors.append(
                f"ids are not stable across fetches ({len(unstable)} differ, e.g. "
                f"{sorted(unstable)[:3]}) — every poll would report these as new"
            )

    if errors:
        print(f"FAIL {name}")
        for error in errors:
            print(f"  - {error}")
        return False

    if not jobs:
        # Not a contract violation, but almost always a wrong search filter.
        print(f"WARN {name}: fetch_jobs() returned 0 jobs in {elapsed:.1f}s — check the query")
        return True

    print(f"ok   {name}: {len(jobs)} jobs, {len(filtered)} after filter, {elapsed:.1f}s")
    for job in filtered[:3]:
        print(f"       {job['title']} — {', '.join(job['locations']) or 'no location'}")
    if len(filtered) > 3:
        print(f"       ... and {len(filtered) - 3} more")
    return True


def main(argv: list[str]) -> int:
    twice = "--twice" in argv
    wanted = [arg for arg in argv if not arg.startswith("--")]

    companies = COMPANIES
    if wanted:
        targets = {name.lower() for name in wanted}
        companies = [
            company
            for company in COMPANIES
            if _module_name(company).lower() in targets
            or company.COMPANY_NAME.lower() in targets
        ]
        if not companies:
            known = ", ".join(_module_name(company) for company in COMPANIES)
            print(f"no company matching {wanted} — known: {known}")
            return 2

    passed = sum(check(company, twice=twice) for company in companies)
    print(f"\n{passed}/{len(companies)} passed")
    return 0 if passed == len(companies) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
