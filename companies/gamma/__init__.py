from ..feeds import ashby_internships_us

COMPANY_NAME = "Gamma"
CAREERS_URL = "https://jobs.ashbyhq.com/gamma"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("gamma")
