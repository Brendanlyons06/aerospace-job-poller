from ..feeds import ashby_internships_us

COMPANY_NAME = "Hadrian"
CAREERS_URL = "https://jobs.ashbyhq.com/hadrian-automation"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("hadrian-automation")
