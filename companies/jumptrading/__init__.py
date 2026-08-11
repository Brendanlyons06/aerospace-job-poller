from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Jump Trading"
CAREERS_URL = "https://www.jumptrading.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("jumptrading")
