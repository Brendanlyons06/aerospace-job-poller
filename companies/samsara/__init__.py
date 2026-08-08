from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Samsara"
CAREERS_URL = "https://www.samsara.com/company/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("samsara")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
