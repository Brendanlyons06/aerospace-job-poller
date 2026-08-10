from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Marqeta"
CAREERS_URL = "https://job-boards.greenhouse.io/marqeta"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("marqeta")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
