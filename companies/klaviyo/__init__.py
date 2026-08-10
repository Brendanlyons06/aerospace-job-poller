from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Klaviyo"
CAREERS_URL = "https://job-boards.greenhouse.io/klaviyo"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("klaviyo")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
