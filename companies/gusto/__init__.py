from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Gusto"
CAREERS_URL = "https://gusto.com/about/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("gusto")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
