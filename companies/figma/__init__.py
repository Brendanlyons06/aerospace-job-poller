from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Figma"
CAREERS_URL = "https://www.figma.com/careers/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("figma")
