from ..feeds import ashby_internships_us

COMPANY_NAME = "AKASA"
CAREERS_URL = "https://jobs.ashbyhq.com/akasa"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("akasa")
