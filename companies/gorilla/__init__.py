from ..feeds import ashby_internships_us

COMPANY_NAME = "Gorilla"
CAREERS_URL = "https://jobs.ashbyhq.com/gorilla"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("gorilla")
