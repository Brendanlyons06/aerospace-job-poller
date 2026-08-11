from ..feeds import ashby_internships_us

COMPANY_NAME = "Helion Energy"
CAREERS_URL = "https://jobs.ashbyhq.com/helion"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("helion")
