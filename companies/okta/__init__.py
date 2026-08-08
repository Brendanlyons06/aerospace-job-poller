from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Okta"
CAREERS_URL = "https://www.okta.com/company/careers/job-listing/"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(CAREERS_URL, r"-(\d+)/")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
