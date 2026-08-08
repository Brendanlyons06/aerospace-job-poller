from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Asana"
CAREERS_URL = "https://asana.com/jobs/all"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(CAREERS_URL, r"/jobs/apply/(\d+)")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
