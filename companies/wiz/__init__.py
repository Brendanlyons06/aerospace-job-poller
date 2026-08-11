from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Wiz"
CAREERS_URL = "https://www.wiz.io/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("wizinc")
