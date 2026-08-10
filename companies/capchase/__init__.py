from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Capchase"
CAREERS_URL = "https://jobs.ashbyhq.com/capchase"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("capchase")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
