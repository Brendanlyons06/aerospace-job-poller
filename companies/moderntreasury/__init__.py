from ..feeds import ashby_internships_us

COMPANY_NAME = "Modern Treasury"
CAREERS_URL = "https://www.moderntreasury.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("moderntreasury")
