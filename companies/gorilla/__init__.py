from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Gorilla"
CAREERS_URL = "https://jobs.ashbyhq.com/gorilla"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("gorilla")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
