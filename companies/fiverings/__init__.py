from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Five Rings"
CAREERS_URL = "https://fiverings.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("fiveringsllc")
