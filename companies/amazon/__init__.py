from ..feeds import amazon_jobs, technical_internships

COMPANY_NAME = "Amazon"
CAREERS_URL = "https://www.amazon.jobs/en/search?base_query=intern"


def fetch_jobs() -> list[dict]:
    return amazon_jobs()


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
