from ..feeds import google_jobs

COMPANY_NAME = "Google"
CAREERS_URL = "https://www.google.com/about/careers/applications/jobs/results/?q=intern"


def fetch_jobs() -> list[dict]:
    return google_jobs()
