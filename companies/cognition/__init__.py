from ..feeds import ashby_internships_us

COMPANY_NAME = "Cognition"
CAREERS_URL = "https://cognition.ai/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("cognition")
