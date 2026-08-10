from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Coupang"
CAREERS_URL = "https://job-boards.greenhouse.io/coupang"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("coupang")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
