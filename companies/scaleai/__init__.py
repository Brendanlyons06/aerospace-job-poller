from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Scale AI"
CAREERS_URL = "https://scale.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("scaleai")
