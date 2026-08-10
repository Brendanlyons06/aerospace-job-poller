from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Dremio"
CAREERS_URL = "https://job-boards.greenhouse.io/dremio"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("dremio")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
