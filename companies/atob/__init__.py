from ..feeds import ashby_internships_us

COMPANY_NAME = "AtoB"
CAREERS_URL = "https://jobs.ashbyhq.com/atob"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("atob")
