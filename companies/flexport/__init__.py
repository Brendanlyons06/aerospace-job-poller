from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Flexport"
CAREERS_URL = "https://job-boards.greenhouse.io/flexport"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("flexport")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
