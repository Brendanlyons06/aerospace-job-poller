from ..feeds import ashby_internships_us

COMPANY_NAME = "Vanta"
CAREERS_URL = "https://jobs.ashbyhq.com/vanta"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("vanta")
