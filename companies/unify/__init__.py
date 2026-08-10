from ..feeds import ashby_internships_us

COMPANY_NAME = "Unify"
CAREERS_URL = "https://jobs.ashbyhq.com/unify"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("unify")
