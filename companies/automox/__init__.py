from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Automox"
CAREERS_URL = "https://job-boards.greenhouse.io/automox"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("automox")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
