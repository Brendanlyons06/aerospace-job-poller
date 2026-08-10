from ..feeds import ashby_internships_us

COMPANY_NAME = "Abridge"
CAREERS_URL = "https://jobs.ashbyhq.com/abridge"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("abridge")
