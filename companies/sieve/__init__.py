from ..feeds import ashby_internships_us

COMPANY_NAME = "Sieve"
CAREERS_URL = "https://www.sievedata.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("sieve")
