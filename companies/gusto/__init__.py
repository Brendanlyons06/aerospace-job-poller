from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Gusto"
CAREERS_URL = "https://gusto.com/about/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("gusto")
