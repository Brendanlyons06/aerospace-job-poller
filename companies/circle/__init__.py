from ..feeds import phenom_internships_us

COMPANY_NAME = "Circle"
CAREERS_URL = "https://careers.circle.com/us/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_internships_us(CAREERS_URL)
