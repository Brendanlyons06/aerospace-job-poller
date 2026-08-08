import re

from ... import http

COMPANY_NAME = "Nuro"


def fetch_jobs() -> list[dict]:
    """Fetch the feed called by Nuro's official careers page."""
    payload = http.get_json(
        "https://boards-api.greenhouse.io/v1/boards/nuro/jobs/?content=true"
    )
    return [
        {
            "id": str(job["id"]),
            "title": job["title"],
            "locations": [
                (job.get("location") or {}).get("name")
            ]
            if (job.get("location") or {}).get("name")
            else [],
            "url": job["absolute_url"],
        }
        for job in payload.get("jobs", [])
    ]


def filter_jobs(jobs: list[dict]) -> list[dict]:
    keywords = ("software", "machine learning", "artificial intelligence", "research")
    return [
        job
        for job in jobs
        if re.search(r"\bintern(?:ship)?s?\b", job["title"], re.IGNORECASE)
        and any(keyword in job["title"].lower() for keyword in keywords)
    ]
