from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Squarespace"
CAREERS_URL = "https://job-boards.greenhouse.io/squarespace"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("squarespace")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
