from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Airbyte"
CAREERS_URL = "https://jobs.ashbyhq.com/airbyte"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("airbyte")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
