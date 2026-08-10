from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Abridge"
CAREERS_URL = "https://jobs.ashbyhq.com/abridge"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("abridge")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
