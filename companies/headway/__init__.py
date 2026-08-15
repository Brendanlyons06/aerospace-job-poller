from ..feeds import ashby_internships_us

COMPANY_NAME = "Headway"
CAREERS_URL = "https://headway.co/about/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("headway")
