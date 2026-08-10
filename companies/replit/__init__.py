from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Replit"
CAREERS_URL = "https://jobs.ashbyhq.com/replit"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("replit")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
