from ..feeds import greenhouse_internships_us

COMPANY_NAME = "DoorDash"
CAREERS_URL = "https://careersatdoordash.com/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("doordashusa")
