from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Kalshi"
CAREERS_URL = "https://jobs.ashbyhq.com/kalshi"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("kalshi")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
