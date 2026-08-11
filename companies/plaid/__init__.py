from ..feeds import lever_internships_us

COMPANY_NAME = "Plaid"
CAREERS_URL = "https://jobs.lever.co/plaid"


def fetch_jobs() -> list[dict]:
    return lever_internships_us("plaid")
