from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Unify"
CAREERS_URL = "https://jobs.ashbyhq.com/unify"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("unify")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
