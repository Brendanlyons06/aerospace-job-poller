from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "OpenTable"
CAREERS_URL = "https://job-boards.greenhouse.io/opentable"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("opentable")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
