from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "HeyMilo"
CAREERS_URL = "https://jobs.ashbyhq.com/heymilo"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("heymilo")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
