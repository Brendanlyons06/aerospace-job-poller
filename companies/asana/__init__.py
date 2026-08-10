from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Asana"
CAREERS_URL = "https://asana.com/jobs/all"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("asana")
