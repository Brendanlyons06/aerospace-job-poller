from ..feeds import ibm_jobs, technical_internships

COMPANY_NAME = "IBM"
CAREERS_URL = "https://www.ibm.com/careers/search?q=intern"


def fetch_jobs() -> list[dict]:
    return ibm_jobs()


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
