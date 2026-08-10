from ..feeds import ashby_internships_us

COMPANY_NAME = "Cohere"
CAREERS_URL = "https://cohere.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("cohere")
