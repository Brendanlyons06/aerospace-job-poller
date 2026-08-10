from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Sumo Logic"
CAREERS_URL = "https://job-boards.greenhouse.io/sumologic"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("sumologic")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
