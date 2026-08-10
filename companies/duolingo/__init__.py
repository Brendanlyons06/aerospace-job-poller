from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Duolingo"
CAREERS_URL = "https://careers.duolingo.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("duolingo")
