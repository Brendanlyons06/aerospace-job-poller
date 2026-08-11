from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Pure Storage"
CAREERS_URL = "https://www.purestorage.com/company/careers.html"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("purestorage")
