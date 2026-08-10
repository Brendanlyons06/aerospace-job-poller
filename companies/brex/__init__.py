from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Brex"
CAREERS_URL = "https://www.brex.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("brex")
