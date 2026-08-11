from ..feeds import ashby_internships_us

COMPANY_NAME = "Base Power"
CAREERS_URL = "https://jobs.ashbyhq.com/base-power"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("base-power")
