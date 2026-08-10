from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Anduril"
CAREERS_URL = "https://job-boards.greenhouse.io/andurilindustries"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("andurilindustries")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
