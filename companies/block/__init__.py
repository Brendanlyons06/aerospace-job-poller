import re

from ... import http
from ...filters import is_us_location

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
        for job_id, title, employee_type, location in re.findall(
            r'\{id:(\d+).*?title:"([^"]+)".*?employeeType:"([^"]+)"'
            r'.*?location:"([^"]*)"',
            page,
            re.S,
        )
        if employee_type == "Intern" and is_us_location(location)
    ]
