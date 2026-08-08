from ..feeds import google_jobs, google_technical_internships

COMPANY_NAME = "Google"
CAREERS_URL = "https://www.google.com/about/careers/applications/jobs/results/?q=intern"


def fetch_jobs() -> list[dict]:
    return google_jobs()


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return google_technical_internships(jobs)
