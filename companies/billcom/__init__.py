from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "BILL"
CAREERS_URL = "https://job-boards.greenhouse.io/billcom"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("billcom")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
