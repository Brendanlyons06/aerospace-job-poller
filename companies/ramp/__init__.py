from ..feeds import ashby_internships_us

COMPANY_NAME = "Ramp"
CAREERS_URL = "https://ramp.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("ramp")
