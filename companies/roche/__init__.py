from ..feeds import phenom_internships_us

COMPANY_NAME = "Roche"
CAREERS_URL = "https://careers.roche.com/global/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_internships_us(CAREERS_URL)
