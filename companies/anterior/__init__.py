from ..feeds import ashby_internships_us

COMPANY_NAME = "Anterior"
CAREERS_URL = "https://www.anterior.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("anterior")
