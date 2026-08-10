from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Attentive"
CAREERS_URL = "https://job-boards.greenhouse.io/attentive"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("attentive")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
