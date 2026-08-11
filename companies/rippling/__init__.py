from ...filters import is_internship_title, is_swe_ml_title
from . import client

COMPANY_NAME = "Rippling"
CAREERS_URL = client.CAREERS_URL


def fetch_jobs() -> list[dict]:
    """Return U.S. software and ML internships from Rippling's own ATS."""
    jobs_by_id = {}
    for hit in client.fetch_job_hits():
        job_id = hit.get("jobId")
        title = hit.get("name")
        url = hit.get("url")
        if (
            not job_id
            or not isinstance(title, str)
            or not url
            or not is_internship_title(title)
            or not is_swe_ml_title(title)
        ):
            continue

        us_locations = [
            location.get("name")
            for location in (hit.get("locations") or [])
            if isinstance(location, dict)
            and location.get("countryCode") == "US"
            and location.get("name")
        ]
        if not us_locations:
            continue

        job = jobs_by_id.setdefault(
            str(job_id),
            {
                "id": str(job_id),
                "title": title,
                "locations": [],
                "url": url,
            },
        )
        job["locations"].extend(
            location for location in us_locations if location not in job["locations"]
        )

    return list(jobs_by_id.values())
