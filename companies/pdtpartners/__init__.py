from ..feeds import greenhouse_internships_us

COMPANY_NAME = "PDT Partners"
CAREERS_URL = "https://www.pdtpartners.com/careers.html"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("pdtpartners")
