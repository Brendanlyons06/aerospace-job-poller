from ..feeds import ashby_internships_us

COMPANY_NAME = "Runpod"
CAREERS_URL = "https://jobs.ashbyhq.com/runpod"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("runpod")
