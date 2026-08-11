from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Cockroach Labs"
CAREERS_URL = "https://www.cockroachlabs.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("cockroachlabs")
