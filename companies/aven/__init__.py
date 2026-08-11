from ..feeds import ashby_internships_us

COMPANY_NAME = "Aven"
CAREERS_URL = "https://www.aven.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("Aven")
