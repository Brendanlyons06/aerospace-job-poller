from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Formlabs"
CAREERS_URL = "https://careers.formlabs.com/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("formlabs")
