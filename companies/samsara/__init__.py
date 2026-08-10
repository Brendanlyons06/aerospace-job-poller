from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Samsara"
CAREERS_URL = "https://www.samsara.com/company/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("samsara")
