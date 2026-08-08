from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Linear"
CAREERS_URL = "https://linear.app/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("linear")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
