"""Reusable filter predicates for normalized job postings.

Nothing here is applied automatically — every site's postings look
different, so each company's filter_jobs() decides what it wants (see
companies/README.md). These are just building blocks to reuse; a company
can call us_only_no_phd() directly, compose the predicates differently, or
ignore this module entirely.

A job dict is expected to have at least: {"title": str, "locations": list[str]}.
Locations come back from career sites as "City, ST" for US postings or
"City, Country" for everything else (e.g. "Austin, TX" vs "London, UK"), so
US-ness is decided by checking for a trailing two-letter US state/territory
code rather than trying to maintain a country blocklist.
"""

import re

PHD_RE = re.compile(r"\bph\.?\s?d\.?\b", re.IGNORECASE)

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR", "VI", "GU",
}

_US_LOCATION_RE = re.compile(r",\s*([A-Za-z]{2})\s*$")


def is_phd_title(title: str) -> bool:
    return bool(PHD_RE.search(title))


def is_us_location(location: str) -> bool:
    match = _US_LOCATION_RE.search(location)
    if not match:
        return False
    return match.group(1).upper() in US_STATE_CODES


def is_us_job(job: dict) -> bool:
    return any(is_us_location(loc) for loc in job.get("locations", []))


def us_only_no_phd(jobs: list[dict]) -> list[dict]:
    """Drop PhD-titled roles and roles with no US location.

    A convenience default for companies that want exactly this combo — not
    applied unless a company's filter_jobs() calls it.
    """
    return [
        job for job in jobs
        if not is_phd_title(job["title"]) and is_us_job(job)
    ]
