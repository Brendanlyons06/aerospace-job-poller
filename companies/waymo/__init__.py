from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Waymo"
CAREERS_URL = "https://careers.withwaymo.com/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("waymo")
