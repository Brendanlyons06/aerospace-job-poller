"""Meta careers adapter: normalizes client.search_jobs() output for watch.py.

This is the interface every company module must expose — see
companies/__init__.py for the registry and companies/README.md for how to
add a new one:
    COMPANY_NAME: str
    fetch_jobs() -> list[dict]        # each dict: id, title, locations, url
    filter_jobs(jobs) -> list[dict]   # optional
"""

from ...filters import is_us_job
from . import client

COMPANY_NAME = "Meta"

# The official search's exact role facet. Country is not represented in the
# public GraphQL search input, so normalized locations are validated below.
ROLES = ["Internship"]


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return [job for job in jobs if is_us_job(job)]


def fetch_jobs() -> list[dict]:
    result = client.search_jobs(roles=ROLES)
    raw_jobs = result["data"]["job_search_with_featured_jobs_v2"]["all_jobs"]
    return [
        {
            "id": job["id"],
            "title": job["title"],
            "locations": job["locations"],
            "url": f"https://www.metacareers.com/jobs/{job['id']}/",
        }
        for job in raw_jobs
    ]
