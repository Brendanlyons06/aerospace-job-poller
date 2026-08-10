from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Lovable"
CAREERS_URL = "https://jobs.ashbyhq.com/lovable"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("lovable")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
