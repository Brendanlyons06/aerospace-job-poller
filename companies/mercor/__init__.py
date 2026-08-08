from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Mercor"
CAREERS_URL = "https://www.mercor.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("mercor")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
