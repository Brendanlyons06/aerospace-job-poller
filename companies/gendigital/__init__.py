from ..feeds import ashby_internships_us

COMPANY_NAME = "Gen Digital"
CAREERS_URL = "https://www.gendigital.com/us/en/careers/"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("gen-digital")
