from ..feeds import ashby_internships_us

COMPANY_NAME = "Browserbase"
CAREERS_URL = "https://jobs.ashbyhq.com/browserbase"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("browserbase")
