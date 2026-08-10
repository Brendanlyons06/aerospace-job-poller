from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "commercetools"
CAREERS_URL = "https://job-boards.greenhouse.io/commercetools"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("commercetools")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
