from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Braze"
CAREERS_URL = "https://job-boards.greenhouse.io/braze"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("braze")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
