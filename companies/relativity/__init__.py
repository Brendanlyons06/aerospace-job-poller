from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Relativity"
CAREERS_URL = "https://job-boards.greenhouse.io/relativity"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("relativity")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
