from ..feeds import ashby_internships_us

COMPANY_NAME = "Patreon"
CAREERS_URL = "https://www.patreon.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("patreon")
