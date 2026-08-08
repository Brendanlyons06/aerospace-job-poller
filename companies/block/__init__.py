import re

from ... import http
from ..feeds import technical_internships

COMPANY_NAME = "Block"
CAREERS_URL = "https://block.xyz/careers/jobs"

def fetch_jobs() -> list[dict]:
    """Read the role records embedded in Block's own careers search page."""
    with http.session() as session:
        response = session.get(CAREERS_URL)
        response.raise_for_status()
        page = response.text
    return [
        {
            "id": job_id,
            "title": title.strip(),
            "locations": [location] if location else [],
            "url": CAREERS_URL,
        }
        for job_id, title, location in re.findall(
            r'\{id:(\d+).*?title:"([^"]+)".*?location:"([^"]*)"', page, re.S
        )
    ]

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
