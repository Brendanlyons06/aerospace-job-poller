from ..feeds import ashby_internships_us

COMPANY_NAME = "Etched"
CAREERS_URL = "https://jobs.ashbyhq.com/etched"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("etched")
