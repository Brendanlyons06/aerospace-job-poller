from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Druva"
CAREERS_URL = "https://job-boards.greenhouse.io/druva"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("druva")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
