from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Toast"
CAREERS_URL = "https://careers.toasttab.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("toast")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
