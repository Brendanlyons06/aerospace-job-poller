from ..feeds import ashby_internships_us

COMPANY_NAME = "Endex"
CAREERS_URL = "https://www.endex.ai/"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("endex")
