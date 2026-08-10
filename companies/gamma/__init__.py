from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Gamma"
CAREERS_URL = "https://jobs.ashbyhq.com/gamma"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("gamma")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
