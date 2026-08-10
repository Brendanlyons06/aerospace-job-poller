from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Fivetran"
CAREERS_URL = "https://job-boards.greenhouse.io/fivetran"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("fivetran")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
