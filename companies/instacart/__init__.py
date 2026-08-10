from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Instacart"
CAREERS_URL = "https://instacart.careers/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("instacart")
