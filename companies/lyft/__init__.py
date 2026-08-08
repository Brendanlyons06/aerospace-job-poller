from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Lyft"
CAREERS_URL = "https://www.lyft.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("lyft")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
