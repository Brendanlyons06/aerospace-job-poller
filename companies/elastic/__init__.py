from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Elastic"
CAREERS_URL = "https://www.elastic.co/about/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("elastic")
