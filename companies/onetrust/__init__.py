from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "OneTrust"
CAREERS_URL = "https://job-boards.greenhouse.io/onetrust"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("onetrust")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
