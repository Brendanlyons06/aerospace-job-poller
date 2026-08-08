from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Ramp"
CAREERS_URL = "https://ramp.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("ramp")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
