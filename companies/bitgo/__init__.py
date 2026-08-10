from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "BitGo"
CAREERS_URL = "https://job-boards.greenhouse.io/bitgo"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("bitgo")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
