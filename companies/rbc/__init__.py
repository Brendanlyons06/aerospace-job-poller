from ..feeds import phenom_internships_us

COMPANY_NAME = "RBC"
CAREERS_URL = "https://jobs.rbc.com/ca/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_internships_us(CAREERS_URL)
