from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Scale AI"
CAREERS_URL = "https://scale.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("scaleai")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
