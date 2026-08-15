from ..feeds import lever_internships_us

COMPANY_NAME = "Anchorage Digital"
CAREERS_URL = "https://www.anchorage.com/careers"


def fetch_jobs() -> list[dict]:
    return lever_internships_us("anchorage")
