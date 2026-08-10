from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "CodeRabbit"
CAREERS_URL = "https://jobs.ashbyhq.com/coderabbit"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("coderabbit")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
