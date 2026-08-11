from ..feeds import greenhouse_internships_us

COMPANY_NAME = "SoFi"
CAREERS_URL = "https://www.sofi.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("sofi")
