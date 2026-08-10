from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Affirm"
CAREERS_URL = "https://www.affirm.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("affirm")
