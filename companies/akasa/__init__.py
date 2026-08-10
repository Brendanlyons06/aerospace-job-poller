from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "AKASA"
CAREERS_URL = "https://jobs.ashbyhq.com/akasa"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("akasa")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
