from ..feeds import ashby_internships_us

COMPANY_NAME = "Radiant"
CAREERS_URL = "https://jobs.ashbyhq.com/radiant-industries"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("radiant-industries")
