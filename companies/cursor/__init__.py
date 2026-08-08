from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Cursor"
CAREERS_URL = "https://cursor.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("cursor")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
