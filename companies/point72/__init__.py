from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Point72"
CAREERS_URL = "https://careers.point72.com/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("point72")
