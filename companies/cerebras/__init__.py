from ..feeds import ashby_internships_us

COMPANY_NAME = "Cerebras"
CAREERS_URL = "https://jobs.ashbyhq.com/cerebras"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("cerebras")
