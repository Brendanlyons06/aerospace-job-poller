from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Postman"
CAREERS_URL = "https://job-boards.greenhouse.io/postman"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("postman")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
