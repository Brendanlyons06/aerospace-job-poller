from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Mercury"
CAREERS_URL = "https://mercury.com/jobs"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("mercury")
