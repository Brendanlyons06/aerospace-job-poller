from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Numeral"
CAREERS_URL = "https://jobs.ashbyhq.com/numeral"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("numeral")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
