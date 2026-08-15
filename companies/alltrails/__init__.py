from ..feeds import lever_internships_us

COMPANY_NAME = "AllTrails"
CAREERS_URL = "https://www.alltrails.com/careers"


def fetch_jobs() -> list[dict]:
    return lever_internships_us("alltrails")
