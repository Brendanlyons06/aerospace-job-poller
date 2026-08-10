from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Vanta"
CAREERS_URL = "https://jobs.ashbyhq.com/vanta"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("vanta")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
