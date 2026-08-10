from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Etched"
CAREERS_URL = "https://jobs.ashbyhq.com/etched"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("etched")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
