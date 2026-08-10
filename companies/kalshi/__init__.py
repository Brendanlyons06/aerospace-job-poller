from ..feeds import ashby_internships_us

COMPANY_NAME = "Kalshi"
CAREERS_URL = "https://jobs.ashbyhq.com/kalshi"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("kalshi")
