from ..feeds import ashby_internships_us

COMPANY_NAME = "Lovable"
CAREERS_URL = "https://jobs.ashbyhq.com/lovable"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("lovable")
