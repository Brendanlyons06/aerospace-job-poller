from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Cribl"
CAREERS_URL = "https://job-boards.greenhouse.io/cribl"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("cribl")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
