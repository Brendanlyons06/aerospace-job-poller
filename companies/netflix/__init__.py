from ..feeds import eightfold_internships_us

COMPANY_NAME = "Netflix"
CAREERS_URL = "https://explore.jobs.netflix.net/careers"


def fetch_jobs() -> list[dict]:
    return eightfold_internships_us("explore.jobs.netflix.net", "netflix.com")
