from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Udemy"
CAREERS_URL = "https://job-boards.greenhouse.io/udemy"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("udemy")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
