from ..feeds import ashby_internships_us

COMPANY_NAME = "Harvey"
CAREERS_URL = "https://jobs.ashbyhq.com/harvey"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("harvey")
