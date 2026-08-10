from ..feeds import ashby_internships_us

COMPANY_NAME = "HeyMilo"
CAREERS_URL = "https://jobs.ashbyhq.com/heymilo"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("heymilo")
