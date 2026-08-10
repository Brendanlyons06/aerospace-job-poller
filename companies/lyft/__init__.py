from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Lyft"
CAREERS_URL = "https://www.lyft.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("lyft")
