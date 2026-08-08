from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Notion"
CAREERS_URL = "https://www.notion.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("notion")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
