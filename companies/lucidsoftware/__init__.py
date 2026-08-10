from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Lucid Software"
CAREERS_URL = "https://job-boards.greenhouse.io/lucidsoftware"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("lucidsoftware")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
