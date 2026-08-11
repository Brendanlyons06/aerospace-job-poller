from ..feeds import ashby_internships_us

COMPANY_NAME = "Alchemy"
CAREERS_URL = "https://www.alchemy.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("alchemy")
