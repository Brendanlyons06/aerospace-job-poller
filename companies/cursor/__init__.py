from ..feeds import ashby_internships_us

COMPANY_NAME = "Cursor"
CAREERS_URL = "https://cursor.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("cursor")
