"""Dashboard-ready classification and normalization for job postings.

Adapters keep their intentionally small, stable contract.  This module adds
derived fields at the persistence boundary so every current and future source
produces the same dashboard shape without duplicating parsing logic.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .filters import is_internship_title, is_us_location


SECTOR_AEROSPACE_DEFENSE = "aerospace-defense"
SECTOR_SPACE = "space-launch-spacecraft"
SECTOR_AIRCRAFT_AUTONOMY = "advanced-aircraft-autonomy"
SECTOR_MANUFACTURING = "advanced-manufacturing-hardware"
SECTOR_ENGINEERING_ORG = "engineering-organization"


_SECTOR_COMPANIES = {
    SECTOR_AEROSPACE_DEFENSE: {
        "Boeing", "Lockheed Martin", "Northrop Grumman", "RTX",
        "GE Aerospace", "General Atomics Aeronautical Systems",
        "General Dynamics", "Honeywell Aerospace", "L3Harris Technologies",
        "BAE Systems", "Textron", "Sierra Nevada Corporation", "Leidos",
        "Anduril Industries", "AeroVironment", "Shield AI", "Kratos Defense",
        "Moog", "Curtiss-Wright", "Parker Hannifin", "Astranis", "Epirus",
        "CACI International", "Mach Industries", "Skydio", "Hadrian", "Saronic",
    },
    SECTOR_SPACE: {
        "SpaceX", "Blue Origin", "Rocket Lab", "Relativity Space", "Stoke Space",
        "Firefly Aerospace", "Axiom Space", "Astrobotic", "Intuitive Machines",
        "Planet Labs", "Millennium Space Systems", "Vast", "Redwire Space",
        "Maxar Space Systems", "Loft Orbital", "Varda Space Industries",
        "Impulse Space", "K2 Space", "True Anomaly", "Apex",
        "Honeybee Robotics", "AstroForge", "Gravitics", "Muon Space", "ispace",
        "Lunar Outpost", "Northwood Space", "GITAI", "SpinLaunch", "Astrolab",
        "Starpath", "Launcher", "Motiv Space Systems",
    },
    SECTOR_AIRCRAFT_AUTONOMY: {
        "Joby Aviation", "Archer Aviation", "Wisk Aero", "BETA Technologies",
        "Boom Supersonic", "Gulfstream Aerospace", "Embraer", "Piper Aircraft",
        "Cirrus Aircraft", "Zipline", "Field AI",
    },
    SECTOR_MANUFACTURING: {
        "Machina Labs", "Karman Space & Defense", "Tesla", "Rivian", "Caterpillar",
        "John Deere", "Cummins", "Bosch", "Siemens", "Eaton", "Emerson",
        "Rockwell Automation", "Applied Materials", "ASML", "Lam Research",
        "Apple Hardware Engineering",
    },
    SECTOR_ENGINEERING_ORG: {
        "NASA", "NASA JPL", "The Aerospace Corporation",
        "Johns Hopkins Applied Physics Laboratory", "MIT Lincoln Laboratory",
        "MITRE", "Sandia National Laboratories",
        "Lawrence Livermore National Laboratory",
        "U.S. Air Force Research Laboratory", "Naval Research Laboratory",
    },
}

COMPANY_SECTORS = {
    company: sector
    for sector, companies in _SECTOR_COMPANIES.items()
    for company in companies
}


_DISCIPLINE_PATTERNS = (
    ("gnc", r"\b(?:gnc|guidance[\s,/-]+navigation(?:[\s,/-]+control)?)\b"),
    ("flight-controls", r"\bflight\s+controls?\b"),
    ("flight-test", r"\bflight\s+test\b"),
    ("flight-sciences", r"\bflight\s+(?:sciences?|dynamics?)\b"),
    ("aerodynamics", r"\baerodynamics?\b"),
    ("aircraft-performance", r"\baircraft\s+performance\b"),
    ("propulsion", r"\bpropulsion\b"),
    ("thermal", r"\bthermal\b"),
    ("structures", r"\bstructures?\s+engineering\b|\bstructural\b"),
    ("systems-integration-test", r"\bsystems?\s+integration(?:\s*&?\s*test)?\b"),
    ("systems", r"\bsystems?\s+(?:engineering|test)\b"),
    ("manufacturing", r"\bmanufacturing\s+engineering\b"),
    ("mechanical-design", r"\bmechanical\s+design\b"),
    ("mechanical", r"\bmechanical\b"),
    ("aerospace", r"\b(?:aerospace|aeronautical)\b"),
    ("vehicle", r"\bvehicle\s+engineering\b"),
    ("quality", r"\bquality\s+engineering\b"),
    ("industrial", r"\bindustrial\s+engineering\b"),
    ("reliability", r"\breliability\s+engineering\b"),
    ("robotics", r"\brobotics?\s+engineering\b"),
    ("autonomy", r"\bautonomy\s+engineering\b"),
    ("controls", r"\bcontrols?\s+engineering\b"),
    ("electrical", r"\b(?:electrical|electronics?|power systems?|radio frequency|rf)\b"),
    ("civil", r"\b(?:civil|geotechnical|transportation|water resources?)\b"),
    ("materials", r"\b(?:materials?|metallurgy|composites?)\s+(?:science|engineering)\b"),
    ("chemical", r"\b(?:chemical|process)\s+engineering\b"),
    ("biomedical", r"\b(?:biomedical|bioengineering)\b"),
    ("data-science", r"\b(?:data science|data scientist|analytics?|machine learning|artificial intelligence|ai/ml)\b"),
    ("software", r"\b(?:software|firmware|embedded systems?|developer|computer science|cybersecurity)\b"),
    ("physics-research", r"\b(?:physics|scientific research|research scientist)\b"),
    ("supply-chain", r"\b(?:supply chain|logistics|procurement)\b"),
    ("business", r"\b(?:business|finance|accounting|marketing|human resources?|operations)\b"),
    ("project", r"\bproject\s+engineering\b"),
    ("test", r"\btest\s+engineering\b"),
)


US_STATE_NAME_TO_CODE = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
    "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
    "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
    "puerto rico": "PR", "u.s. virgin islands": "VI", "guam": "GU",
}
US_STATE_CODES = frozenset(US_STATE_NAME_TO_CODE.values())
_COUNTRY_LABELS = {
    "us", "usa", "u.s.", "u.s.a.", "united states",
    "united states of america",
}


def _clean_city_name(value: str) -> str | None:
    """Drop ATS site codes and facility details from a city-like value."""
    text = re.sub(r"\s*~.*$", "", value or "").strip()
    text = re.sub(r"\s*\([A-Z0-9 -]{1,8}\)\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"-(?:[A-Z]\d{1,4}|\d{1,4})$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" ,-~")
    if not text:
        return None
    return text.title() if text.isupper() else text


def normalize_location_parts(label: str, details: dict | None = None) -> tuple[str | None, str | None]:
    """Extract a reusable city/state pair from human or ATS location labels."""
    details = details or {}
    supplied_city = details.get("city")
    supplied_state = details.get("state")
    if isinstance(supplied_state, str):
        supplied_state = US_STATE_NAME_TO_CODE.get(
            supplied_state.strip().lower(), supplied_state.strip().upper()
        )
    if isinstance(supplied_city, str) and supplied_city.strip():
        return _clean_city_name(supplied_city), supplied_state

    text = (label or "").strip()
    ats_match = re.match(r"^US-([A-Z]{2})-(.+)$", text, re.IGNORECASE)
    if ats_match:
        return _clean_city_name(ats_match.group(2)), supplied_state or ats_match.group(1).upper()

    workday_match = re.fullmatch(
        r"United States(?: of America)?-([^-]+)-(.+)", text, re.IGNORECASE
    )
    if workday_match:
        state_name = workday_match.group(1).strip()
        state = US_STATE_NAME_TO_CODE.get(state_name.lower(), state_name.upper())
        return _clean_city_name(workday_match.group(2)), supplied_state or state

    tokens = [
        part.strip()
        for part in re.split(r"\s*[,|;]\s*", re.sub(r"\s*~.*$", "", text))
        if part.strip()
    ]
    useful = [part for part in tokens if part.lower().strip(". ") not in _COUNTRY_LABELS]
    for index, token in enumerate(useful):
        lowered = token.lower().strip(". ")
        state = token.upper() if token.upper() in US_STATE_CODES else US_STATE_NAME_TO_CODE.get(lowered)
        if not state:
            continue
        city = useful[index - 1] if index > 0 else (useful[index + 1] if index + 1 < len(useful) else "")
        return _clean_city_name(city), supplied_state or state

    return None, supplied_state


def company_sector(company: str) -> str:
    """Return the stable dashboard sector for a company."""
    return COMPANY_SECTORS.get(company, "other-engineering")


def classify_discipline(title: str) -> str:
    """Choose one primary discipline for filtering and grouping."""
    for discipline, pattern in _DISCIPLINE_PATTERNS:
        if re.search(pattern, title or "", re.IGNORECASE):
            return discipline
    return "general-engineering"


def classify_work_mode(title: str, locations: list[str]) -> str | None:
    """Infer work mode only from explicit title/location language."""
    text = " ".join([title or "", *locations]).lower()
    if re.search(r"\bhybrid\b", text):
        return "hybrid"
    if re.search(r"\b(?:remote|work from home|telecommut)\b", text):
        return "remote"
    if locations:
        return "on-site"
    return None


def normalize_work_mode(value: str | None, title: str, locations: list[str]) -> str | None:
    if isinstance(value, str) and value.strip():
        lowered = value.strip().lower().replace("_", "-")
        if "hybrid" in lowered:
            return "hybrid"
        if "remote" in lowered:
            return "remote"
        if lowered in {"onsite", "on-site", "in-person", "office"}:
            return "on-site"
    return classify_work_mode(title, locations)


def normalize_employment_type(value: str | None, title: str) -> str | None:
    text = (value or "").strip().lower()
    combined = f"{text} {title or ''}".lower()
    if re.search(r"\bco[ -]?op\b", combined):
        return "co-op"
    if "intern" in text or (not text and is_internship_title(title)):
        return "internship"
    if "full" in text:
        return "full-time"
    if "part" in text:
        return "part-time"
    return text or None


def normalize_timestamp(value) -> str | None:
    """Normalize ISO strings or Unix seconds/milliseconds to UTC ISO text."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def _number(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def structured_location(label: str, details: dict | None = None) -> dict:
    """Parse a display label while preserving optional source coordinates."""
    details = details or {}
    city, state = normalize_location_parts(label, details)

    latitude = details.get("latitude")
    longitude = details.get("longitude")
    try:
        latitude = float(latitude) if latitude is not None else None
        longitude = float(longitude) if longitude is not None else None
    except (TypeError, ValueError):
        latitude = longitude = None

    return {
        "label": label,
        "city": city,
        "state": state,
        "country": details.get("country") or ("US" if state or is_us_location(label) else None),
        "latitude": latitude,
        "longitude": longitude,
    }


def enrich_job(company: str, job: dict) -> dict:
    """Return persistence metadata without mutating the adapter result."""
    locations = list(job.get("locations") or [])
    supplied_details = job.get("location_details") or []
    details_by_label = {
        item.get("label"): item
        for item in supplied_details
        if isinstance(item, dict) and item.get("label")
    }
    compensation = job.get("compensation") or {}
    employment_type = normalize_employment_type(
        job.get("employment_type"), job.get("title", "")
    )

    return {
        "sector": company_sector(company),
        "discipline": job.get("discipline") or classify_discipline(job.get("title", "")),
        "employment_type": employment_type,
        "work_mode": normalize_work_mode(
            job.get("work_mode"), job.get("title", ""), locations
        ),
        "posted_at": normalize_timestamp(job.get("posted_at")),
        "closes_at": normalize_timestamp(job.get("closes_at")),
        "compensation_min": _number(compensation.get("min")),
        "compensation_max": _number(compensation.get("max")),
        "compensation_currency": compensation.get("currency"),
        "compensation_period": compensation.get("period"),
        "structured_locations": [
            structured_location(label, details_by_label.get(label))
            for label in locations
        ],
    }
