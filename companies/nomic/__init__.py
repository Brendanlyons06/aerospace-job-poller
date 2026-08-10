from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Nomic"
CAREERS_URL = "https://jobs.ashbyhq.com/nomic"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("nomic")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
