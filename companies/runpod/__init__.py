from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Runpod"
CAREERS_URL = "https://jobs.ashbyhq.com/runpod"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("runpod")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
