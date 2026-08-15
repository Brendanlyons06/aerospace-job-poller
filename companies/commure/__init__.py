from ..feeds import ashby_internships_us

COMPANY_NAME = "Commure"
CAREERS_URL = "https://www.commure.com/careers"


def fetch_jobs() -> list[dict]:
    # Ashby tokens are case-sensitive: "Commure", not "commure".
    return ashby_internships_us("Commure")
