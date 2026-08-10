from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Braintrust"
CAREERS_URL = "https://jobs.ashbyhq.com/braintrust"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("braintrust")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
