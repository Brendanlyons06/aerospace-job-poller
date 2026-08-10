import json

from ... import http
from ...filters import is_us_location, swe_ml_jobs

COMPANY_NAME = "Snap Inc."
CAREERS_URL = "https://careers.snap.com/jobs"


def fetch_jobs() -> list[dict]:
    """Apply the exact Type and Location fields used by Snap's filter UI."""
    with http.session() as session:
        response = session.get(CAREERS_URL)
        response.raise_for_status()
    marker = "window.ASYNC_DATA_CONTROLLER_CACHE = "
    start = response.text.find(marker)
    if start < 0:
        raise ValueError("Snap careers data was not present")
    cache = json.JSONDecoder().raw_decode(response.text, start + len(marker))[0]
    records = next(
        value.get("data", {}).get("body", [])
        for key, value in cache.items()
        if key.startswith("jobs--")
    )
    jobs = []
    for record in records:
        job = record.get("_source") or {}
        if job.get("employment_type") != "Intern":
            continue
        locations = [
            office.get("location") or office.get("name")
            for office in (job.get("offices") or [])
            if is_us_location(office.get("location") or office.get("name") or "")
        ]
        if not locations:
            continue
        jobs.append(
            {
                "id": str(job.get("id") or record.get("_id")),
                "title": job["title"],
                "locations": list(dict.fromkeys(locations)),
                "url": job.get("absolute_url") or f"{CAREERS_URL}/job?id={job['id']}",
            }
        )
    return swe_ml_jobs(jobs)
