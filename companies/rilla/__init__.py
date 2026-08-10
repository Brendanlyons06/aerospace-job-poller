from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Rilla"
CAREERS_URL = "https://jobs.ashbyhq.com/rilla"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("rilla")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
