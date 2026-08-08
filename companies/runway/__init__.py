from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Runway"
CAREERS_URL = "https://runwayml.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("runway")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
