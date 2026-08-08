"""Meta careers adapter: normalizes client.search_jobs() output for watch.py.

This is the interface every company module must expose — see
companies/__init__.py for the registry and companies/README.md for how to
add a new one:
    COMPANY_NAME: str
    fetch_jobs() -> list[dict]        # each dict: id, title, locations, url
    filter_jobs(jobs) -> list[dict]   # optional
"""

from ...filters import us_only_no_phd
from . import client

COMPANY_NAME = "Meta"

# Software + AI internships. See client.py for how these map onto the
# CareersJobSearchResultsV2DataQuery search_input (roles/teams captured
# live from companies/metacareers/2nd.har).
ROLES = ["Internship"]
TEAMS = ["Software Engineering", "Artificial Intelligence"]

# Meta posts plenty of non-US and PhD-only roles under the same search —
# filter those out. Other companies aren't obligated to reuse this.
filter_jobs = us_only_no_phd


def fetch_jobs() -> list[dict]:
    result = client.search_jobs(roles=ROLES, teams=TEAMS)
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
