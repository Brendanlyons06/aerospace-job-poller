from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Modal"
CAREERS_URL = "https://modal.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("modal")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
