from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "New Relic"
CAREERS_URL = "https://job-boards.greenhouse.io/newrelic"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("newrelic")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
