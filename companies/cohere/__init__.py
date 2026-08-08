from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Cohere"
CAREERS_URL = "https://cohere.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("cohere")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
