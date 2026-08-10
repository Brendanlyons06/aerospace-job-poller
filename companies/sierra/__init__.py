from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Sierra"
CAREERS_URL = "https://jobs.ashbyhq.com/sierra"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("sierra")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
