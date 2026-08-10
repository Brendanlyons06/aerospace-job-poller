from ..feeds import ashby_internships_us

COMPANY_NAME = "Anrok"
CAREERS_URL = "https://jobs.ashbyhq.com/anrok"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("anrok")
