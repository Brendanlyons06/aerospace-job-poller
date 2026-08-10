from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Harvey"
CAREERS_URL = "https://jobs.ashbyhq.com/harvey"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("harvey")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
