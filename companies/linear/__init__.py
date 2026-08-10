from ..feeds import ashby_internships_us

COMPANY_NAME = "Linear"
CAREERS_URL = "https://linear.app/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("linear")
