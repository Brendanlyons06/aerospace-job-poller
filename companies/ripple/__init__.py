from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Ripple"
CAREERS_URL = "https://ripple.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("ripple")
