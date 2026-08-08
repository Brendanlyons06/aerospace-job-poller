import re

from ... import http

COMPANY_NAME = "Cloudflare"


def fetch_jobs() -> list[dict]:
    """Fetch the public feed called by Cloudflare's official careers page."""
    payload = http.get_json("https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs")
    jobs = []
    for job in payload.get("jobs", []):
        locations = []
        location = (job.get("location") or {}).get("name")
        if location:
            locations.append(location)
        for metadata in job.get("metadata", []):
            if metadata.get("name") == "Job Posting Location":
                value = metadata.get("value")
                locations.extend(value if isinstance(value, list) else [value])
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": list(dict.fromkeys(locations)),
                "url": job["absolute_url"],
            }
        )
    return jobs


def filter_jobs(jobs: list[dict]) -> list[dict]:
    keywords = ("software", "machine learning", "artificial intelligence", "research")
    return [
        job
        for job in jobs
        if re.search(r"\bintern(?:ship)?s?\b", job["title"], re.IGNORECASE)
        and any(keyword in job["title"].lower() for keyword in keywords)
    ]
