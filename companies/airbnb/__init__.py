from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Airbnb"
CAREERS_URL = "https://careers.airbnb.com/positions/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("airbnb")
