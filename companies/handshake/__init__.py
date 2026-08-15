from ..feeds import ashby_internships_us

COMPANY_NAME = "Handshake"
CAREERS_URL = "https://joinhandshake.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("handshake")
