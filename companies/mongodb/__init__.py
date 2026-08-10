from ..feeds import greenhouse_internships_us

COMPANY_NAME = "MongoDB"
CAREERS_URL = "https://www.mongodb.com/company/careers/see-jobs"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("mongodb")
