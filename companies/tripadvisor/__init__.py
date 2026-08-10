from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Tripadvisor"
CAREERS_URL = "https://job-boards.greenhouse.io/tripadvisor"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("tripadvisor")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
