from ..feeds import phenom_internships_us

COMPANY_NAME = "Thermo Fisher Scientific"
CAREERS_URL = "https://jobs.thermofisher.com/global/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_internships_us(CAREERS_URL)
