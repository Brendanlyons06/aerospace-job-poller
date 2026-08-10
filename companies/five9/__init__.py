from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Five9"
CAREERS_URL = "https://job-boards.greenhouse.io/five9"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("five9")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
