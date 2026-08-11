from ..feeds import ashby_internships_us

COMPANY_NAME = "Second Dinner"
CAREERS_URL = "https://jobs.ashbyhq.com/SecondDinner"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("SecondDinner")
