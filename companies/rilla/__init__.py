from ..feeds import ashby_internships_us

COMPANY_NAME = "Rilla"
CAREERS_URL = "https://jobs.ashbyhq.com/rilla"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("rilla")
