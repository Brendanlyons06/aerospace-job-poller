from ... import http
from ...filters import is_us_location, swe_ml_jobs

COMPANY_NAME = "Roblox"


def fetch_jobs() -> list[dict]:
    """Fetch the JSON feed used by Roblox's official careers page."""
    postings = http.get_json("https://d32kbl9jppd7az.cloudfront.net/careers/jobs.json")
    jobs = [
        {
            "id": str(job["id"]),
            "title": job["title"].strip(),
            "locations": [job["location"]] if job.get("location") else [],
            "url": f"https://careers.roblox.com/jobs/{job['id']}",
        }
        for job in postings
        if job.get("employment_type") == "Intern"
        and is_us_location(job.get("location", ""))
    ]
    return swe_ml_jobs(jobs)
