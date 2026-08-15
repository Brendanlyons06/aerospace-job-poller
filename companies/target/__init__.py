from ..feeds import workday_internships_us

COMPANY_NAME = "Target"
CAREERS_URL = "https://corporate.target.com/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("target", "targetcareers")
