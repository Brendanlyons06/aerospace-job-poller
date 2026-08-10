from ..feeds import ashby_internships_us

COMPANY_NAME = "Braintrust"
CAREERS_URL = "https://jobs.ashbyhq.com/braintrust"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("braintrust")
