from ..feeds import ashby_internships_us

COMPANY_NAME = "Airbyte"
CAREERS_URL = "https://jobs.ashbyhq.com/airbyte"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("airbyte")
