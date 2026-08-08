from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Elastic"
CAREERS_URL = "https://www.elastic.co/about/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("elastic")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
