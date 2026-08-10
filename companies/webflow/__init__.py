from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Webflow"
CAREERS_URL = "https://job-boards.greenhouse.io/webflow"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("webflow")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
