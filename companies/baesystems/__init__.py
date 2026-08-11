from ..feeds import phenom_internships_us

COMPANY_NAME = "BAE Systems"
CAREERS_URL = "https://jobs.baesystems.com/global/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_internships_us(CAREERS_URL)
