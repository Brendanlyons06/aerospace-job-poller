import re

from ... import http

COMPANY_NAME = "Roblox"


def fetch_jobs() -> list[dict]:
    """Fetch the JSON feed used by Roblox's official careers page."""
    postings = http.get_json("https://d32kbl9jppd7az.cloudfront.net/careers/jobs.json")
    return [
        {
            "id": str(job["id"]),
            "title": job["title"].strip(),
            "locations": [job["location"]] if job.get("location") else [],
            "url": f"https://careers.roblox.com/jobs/{job['id']}",
        }
        for job in postings
    ]


def filter_jobs(jobs: list[dict]) -> list[dict]:
    keywords = ("software", "machine learning", "artificial intelligence", "research")
    return [
        job
        for job in jobs
        if re.search(r"\bintern(?:ship)?s?\b", job["title"], re.IGNORECASE)
        and any(keyword in job["title"].lower() for keyword in keywords)
    ]
