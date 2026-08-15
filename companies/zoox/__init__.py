from ..feeds import lever_internships_us

COMPANY_NAME = "Zoox"
CAREERS_URL = "https://zoox.com/careers"


def fetch_jobs() -> list[dict]:
    return lever_internships_us("zoox")
