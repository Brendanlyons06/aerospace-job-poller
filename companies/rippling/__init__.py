"""Rippling jobs from the Algolia index behind its own careers board."""

from ...filters import is_internship_title, is_swe_ml_title
from . import client

COMPANY_NAME = "Rippling"
CAREERS_URL = "https://www.rippling.com/careers/open-roles"


def fetch_jobs() -> list[dict]:
    """Merge per-location Algolia hits into one posting per stable jobId."""
    merged: dict[str, dict] = {}
    for hit in client.search_hits():
        job_id = hit.get("jobId")
        if not job_id:
            continue
        job = merged.setdefault(
            str(job_id),
            {
                "id": str(job_id),
                "title": (hit.get("name") or "").strip(),
                "locations": [],
                "url": hit.get("url")
                or f"https://ats.rippling.com/rippling/jobs/{job_id}",
            },
        )
        for location in hit.get("locations") or []:
            if location.get("countryCode") != "US":
                continue
            name = location.get("name")
            if name and name not in job["locations"]:
                job["locations"].append(name)
    # The index has no structured employment type, so internships are
    # title-identified; US-ness came from the structured country code above.
    return [
        job
        for job in merged.values()
        if job["locations"]
        and is_internship_title(job["title"])
        and is_swe_ml_title(job["title"])
    ]
