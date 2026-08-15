from ..feeds import greenhouse_internships_us

COMPANY_NAME = "GoDaddy"
CAREERS_URL = "https://careers.godaddy/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("godaddy")
