from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Liftoff"
CAREERS_URL = "https://job-boards.greenhouse.io/liftoff"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("liftoff")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
