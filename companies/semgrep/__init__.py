from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Semgrep"
CAREERS_URL = "https://jobs.ashbyhq.com/semgrep"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("semgrep")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
