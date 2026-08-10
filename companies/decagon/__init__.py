from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Decagon"
CAREERS_URL = "https://jobs.ashbyhq.com/decagon"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("decagon")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
