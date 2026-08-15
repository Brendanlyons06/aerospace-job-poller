from ..feeds import ashby_internships_us

COMPANY_NAME = "Crusoe"
CAREERS_URL = "https://crusoe.ai/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("Crusoe")
