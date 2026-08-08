from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Duolingo"
CAREERS_URL = "https://careers.duolingo.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("duolingo")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
