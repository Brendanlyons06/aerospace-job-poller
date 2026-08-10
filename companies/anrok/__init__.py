from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Anrok"
CAREERS_URL = "https://jobs.ashbyhq.com/anrok"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("anrok")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
