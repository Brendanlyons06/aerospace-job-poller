from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Chime"
CAREERS_URL = "https://job-boards.greenhouse.io/chime"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("chime")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
