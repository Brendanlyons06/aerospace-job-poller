from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Airtable"
CAREERS_URL = "https://job-boards.greenhouse.io/airtable"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("airtable")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
