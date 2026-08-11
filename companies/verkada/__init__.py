from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Verkada"
CAREERS_URL = "https://www.verkada.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("verkada")
