from ..feeds import phenom_jobs, technical_internships

COMPANY_NAME = "Cisco"
CAREERS_URL = "https://careers.cisco.com/global/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_jobs(CAREERS_URL)


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
