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
SWE_ML_RE = re.compile(
    r"(?:"
    r"\bsoftware(?:[\s-]+development)?[\s-]+(?:engineer(?:ing)?|developer)\b|"
    r"\bsoftware(?=[\s-]+(?:intern(?:ship)?s?|co[\s-]?op))\b|"
    r"\b(?:swe|sde)\b|"
    # Quant firms title their software-engineering track "Quantitative
    # Developer"; trader/researcher tracks stay excluded below.
    r"\bquant(?:itative)?[\s-]+dev(?:eloper)?\b|"
    r"\bmachine[\s-]+learning\b|"
    r"\bml\b|"
    r"\bai\s*[/&+-]\s*ml\b|"
    r"\bartificial[\s-]+intelligence\b|"
    r"\bai(?=[\s-]+(?:engineer(?:ing)?|research|intern(?:ship)?s?|co[\s-]?op))\b"
    r")",
    re.IGNORECASE,
)

# Engineering roles that are useful for the aerospace, space, defense,
# robotics, and advanced-manufacturing search.  Keep this title-based rather
# than matching descriptions: the supported job-board feeds do not all
# expose descriptions, and a stable title is much less likely to alert on a
# software role that merely mentions a spacecraft in its copy.
AEROSPACE_MECHANICAL_RE = re.compile(
    r"(?:"
    r"\baerospace\b|\baeronautical\b|"
    r"\bmechanical(?:\s+design)?\b|"
    r"\bflight\s+(?:sciences?|controls?|test|dynamics?)\b|"
    r"\bgnc\b|\bguidance[\s,/-]+navigation(?:[\s,/-]+control)?\b|"
    r"\baerodynamics?\b|\baircraft\s+performance\b|"
    r"\bvehicle\s+engineering\b|\bstructures?\s+engineering\b|"
    r"\bpropulsion\b|\bthermal\b|"
    r"\bsystems?\s+(?:engineering|integration(?:\s*&?\s*test)?|test)\b|"
    r"\bproject\s+engineering\b|\bmanufacturing\s+engineering\b|"
    r"\bquality\s+engineering\b|\bindustrial\s+engineering\b|"
    r"\breliability\s+engineering\b|\btest\s+engineering\b|"
    r"\bcontrols?\s+engineering\b|\brobotics?\s+engineering\b|"
    r"\bautonomy\s+engineering\b"
    r")",
    re.IGNORECASE,
)

AEROSPACE_SOFTWARE_RE = re.compile(
    r"\b(?:software|web|frontend|backend|full[\s-]?stack|"
    r"machine[\s-]?learning|data\s+science|computer\s+science|IT)\b",
    re.IGNORECASE,
)

# Some aerospace employers post one intentionally broad internship for every
# engineering discipline. Keep this separate from the main predicate so only
# known aerospace boards opt into it; applying it to all 300+ companies would
# make generic civil/electrical postings noisy.
GENERIC_ENGINEERING_INTERNSHIP_RE = re.compile(
    r"^(?:(?:spring|summer|fall|winter)\s+\d{4}\s+)?"
    r"(?:graduate\s+engineer|engineering)\s+intern(?:ship)?"
    r"(?:/co[\s-]?op)?(?:\s+-\s+undergraduate)?$",
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


def is_swe_ml_title(title: str) -> bool:
    """Return whether a title is specifically in software or ML/AI work.

    Generic engineering, data, research, product, and hardware titles are
    deliberately excluded. The poller is intended to alert only for software
    engineering and machine-learning internships, not every technical role.
    """
    return isinstance(title, str) and bool(SWE_ML_RE.search(title))


def is_aerospace_mechanical_title(title: str) -> bool:
    """Return whether a title names an aerospace/mechanical-style role."""
    return (
        isinstance(title, str)
        and bool(AEROSPACE_MECHANICAL_RE.search(title))
        and not bool(AEROSPACE_SOFTWARE_RE.search(title))
    )


def is_generic_engineering_internship_title(title: str) -> bool:
    """Recognize deliberately cross-discipline engineering internships."""
    return isinstance(title, str) and bool(
        GENERIC_ENGINEERING_INTERNSHIP_RE.fullmatch(title.strip())
    )


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
    """Strict title/location fallback for the target internship search."""
    return [
        job for job in jobs
        if is_internship_title(job.get("title", ""))
        and is_swe_ml_title(job.get("title", ""))
        and is_us_job(job)
    ]


def swe_ml_jobs(jobs: list[dict]) -> list[dict]:
    """Keep target-role jobs when type and country were proven structurally."""
    return [job for job in jobs if is_swe_ml_title(job.get("title", ""))]


def aerospace_mechanical_jobs(
    jobs: list[dict],
    *,
    require_internship: bool = True,
    require_us: bool = True,
) -> list[dict]:
    """Keep aerospace/mechanical engineering postings for the target profile.

    ``require_us=False`` is useful for boards such as SpaceX whose postings
    use a company-wide location label (for example, ``Any SpaceX Site``)
    instead of a country or city that :func:`is_us_location` can recognize.
    """
    result = []
    for job in jobs:
        title = job.get("title", "")
        if require_internship and not is_internship_title(title):
            continue
        if not is_aerospace_mechanical_title(title):
            continue
        if require_us and not is_us_job(job):
            continue
        result.append(job)
    return result


def aerospace_mechanical_internships_us(jobs: list[dict]) -> list[dict]:
    """Strict U.S. aerospace/mechanical internship fallback filter."""
    return aerospace_mechanical_jobs(jobs)


def us_only_no_phd(jobs: list[dict]) -> list[dict]:
    """Drop PhD-titled roles and roles with no US location.

    A convenience default for companies that want exactly this combo — not
    applied unless a company's filter_jobs() calls it.
    """
    return [
        job for job in jobs
        if not is_phd_title(job["title"]) and is_us_job(job)
    ]
