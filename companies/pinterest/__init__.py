from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Pinterest"
CAREERS_URL = "https://www.pinterestcareers.com/jobs/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("pinterest")
