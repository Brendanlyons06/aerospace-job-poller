from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Airbnb"
CAREERS_URL = "https://careers.airbnb.com/positions/"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(CAREERS_URL, r"/positions/(\d+)/")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
