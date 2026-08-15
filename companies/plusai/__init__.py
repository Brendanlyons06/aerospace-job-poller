from ..feeds import lever_internships_us

COMPANY_NAME = "Plus AI"
CAREERS_URL = "https://plus.ai/careers"


def fetch_jobs() -> list[dict]:
    # Plus's Lever board token is "plus-2".
    return lever_internships_us("plus-2")
