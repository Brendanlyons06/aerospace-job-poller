from ..feeds import workday_internships_us

COMPANY_NAME = "Adobe"
CAREERS_URL = "https://careers.adobe.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("adobe", "external_experienced")
