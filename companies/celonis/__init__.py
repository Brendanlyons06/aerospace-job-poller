from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Celonis"
CAREERS_URL = "https://job-boards.greenhouse.io/celonis"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("celonis")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
