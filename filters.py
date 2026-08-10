"""Reusable filter predicates for normalized job postings.

Nothing here is applied automatically — every site's postings look
different, so each company's filter_jobs() decides what it wants (see
companies/README.md). These are just building blocks to reuse; a company
can call us_only_no_phd() directly, compose the predicates differently, or
ignore this module entirely.

A job dict is expected to have at least: {"title": str, "locations": list[str]}.
Locations come back in several forms (``Austin, TX``, ``US, California``,
``Remote - United States``), so the predicates understand both country names
and state/territory names and abbreviations.
"""

import re

PHD_RE = re.compile(r"\bph\.?\s?d\.?\b", re.IGNORECASE)
INTERNSHIP_RE = re.compile(
    r"\b(?:intern(?:ship)?s?|co[\s-]?op(?:erative)?|student researcher)\b",
    re.IGNORECASE,
)

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR", "VI", "GU",
}

US_STATE_NAMES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming", "district of columbia",
    "puerto rico", "u.s. virgin islands", "guam",
}

_US_COUNTRY_RE = re.compile(
    r"(?:\bunited states(?: of america)?\b|"
    r"(?<![A-Za-z])(?:US|USA|U\.S\.|U\.S\.A\.?)(?![A-Za-z]))",
    re.IGNORECASE,
)
_LOCATION_PART_RE = re.compile(r"\s*(?:,|/|\||;| - )\s*")


def is_phd_title(title: str) -> bool:
    return bool(PHD_RE.search(title))


def is_internship_title(title: str) -> bool:
    """Return whether a title explicitly describes an internship/co-op."""
    return bool(INTERNSHIP_RE.search(title))


def is_us_location(location: str) -> bool:
    """Recognize the country and region labels used by supported job boards."""
    if not isinstance(location, str) or not location.strip():
        return False
    if _US_COUNTRY_RE.search(location):
        return True
    parts = [part.strip(" ()").lower() for part in _LOCATION_PART_RE.split(location)]
    if any(part in US_STATE_NAMES for part in parts):
        return True
    return any(part.upper() in US_STATE_CODES for part in parts)


def is_us_job(job: dict) -> bool:
    return any(is_us_location(loc) for loc in job.get("locations", []))


def internships_in_us(jobs: list[dict]) -> list[dict]:
    """Strict fallback for sites without server-side type/country facets."""
    return [
        job for job in jobs
        if is_internship_title(job.get("title", "")) and is_us_job(job)
    ]


def us_only_no_phd(jobs: list[dict]) -> list[dict]:
    """Drop PhD-titled roles and roles with no US location.

    A convenience default for companies that want exactly this combo — not
    applied unless a company's filter_jobs() calls it.
    """
    return [
        job for job in jobs
        if not is_phd_title(job["title"]) and is_us_job(job)
    ]
