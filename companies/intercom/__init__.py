from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Intercom"
CAREERS_URL = "https://job-boards.greenhouse.io/intercom"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("intercom")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
