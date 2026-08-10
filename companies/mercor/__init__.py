from ..feeds import ashby_internships_us

COMPANY_NAME = "Mercor"
CAREERS_URL = "https://www.mercor.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("mercor")
