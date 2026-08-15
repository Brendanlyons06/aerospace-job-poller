from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Addepar"
CAREERS_URL = "https://addepar.com/careers"


def fetch_jobs() -> list[dict]:
    # Addepar's Greenhouse board token is "addepar1", not "addepar".
    return greenhouse_internships_us("addepar1")
