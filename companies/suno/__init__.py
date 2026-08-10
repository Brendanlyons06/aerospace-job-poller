from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Suno"
CAREERS_URL = "https://jobs.ashbyhq.com/suno"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("suno")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
