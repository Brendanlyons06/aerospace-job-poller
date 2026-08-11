from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Epirus"
CAREERS_URL = "https://www.epirusinc.com/open-roles"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("epirus")
