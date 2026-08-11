from ..feeds import ashby_internships_us

COMPANY_NAME = "Illumio"
CAREERS_URL = "https://www.illumio.com/company/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("illumio")
