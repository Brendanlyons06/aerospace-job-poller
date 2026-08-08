from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Affirm"
CAREERS_URL = "https://www.affirm.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("affirm")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
