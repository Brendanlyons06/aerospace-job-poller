from ..feeds import ashby_internships_us

COMPANY_NAME = "Saronic"
CAREERS_URL = "https://jobs.ashbyhq.com/saronic"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("saronic")
