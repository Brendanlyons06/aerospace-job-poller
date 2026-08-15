from ..feeds import workday_internships_us

COMPANY_NAME = "Proofpoint"
CAREERS_URL = "https://www.proofpoint.com/us/company/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("proofpoint", "proofpointcareers")
