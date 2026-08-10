from ..feeds import ashby_internships_us

COMPANY_NAME = "Baseten"
CAREERS_URL = "https://jobs.ashbyhq.com/baseten"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("baseten")
