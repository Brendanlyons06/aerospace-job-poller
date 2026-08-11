from ..feeds import ashby_internships_us

COMPANY_NAME = "Fab2 (Atomic Semi)"
CAREERS_URL = "https://fab2.com/careers/"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("fab2")
