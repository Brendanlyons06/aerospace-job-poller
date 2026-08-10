from ..feeds import ashby_internships_us

COMPANY_NAME = "Runway"
CAREERS_URL = "https://runwayml.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("runway")
