from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Robinhood"
CAREERS_URL = "https://job-boards.greenhouse.io/robinhood"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("robinhood")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
