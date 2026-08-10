from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Parallel"
CAREERS_URL = "https://jobs.ashbyhq.com/parallel"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("parallel")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
