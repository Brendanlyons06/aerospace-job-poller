from ..feeds import ashby_internships_us

COMPANY_NAME = "Hightouch"
CAREERS_URL = "https://jobs.ashbyhq.com/hightouch"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("hightouch")
