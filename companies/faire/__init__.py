from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Faire"
CAREERS_URL = "https://job-boards.greenhouse.io/faire"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("faire")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
