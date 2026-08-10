from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Saronic"
CAREERS_URL = "https://jobs.ashbyhq.com/saronic"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("saronic")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
