from ..feeds import ashby_internships_us

COMPANY_NAME = "Zapier"
CAREERS_URL = "https://zapier.com/jobs"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("zapier")
