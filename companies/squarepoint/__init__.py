from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Squarepoint Capital"
CAREERS_URL = "https://www.squarepoint-capital.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("squarepointcapital")
