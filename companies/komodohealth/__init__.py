from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Komodo Health"
CAREERS_URL = "https://job-boards.greenhouse.io/komodohealth"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("komodohealth")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
