from ..feeds import ashby_internships_us

COMPANY_NAME = "Sierra"
CAREERS_URL = "https://jobs.ashbyhq.com/sierra"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("sierra")
