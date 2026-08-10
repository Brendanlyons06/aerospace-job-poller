from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Hightouch"
CAREERS_URL = "https://jobs.ashbyhq.com/hightouch"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("hightouch")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
