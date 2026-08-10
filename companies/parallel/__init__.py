from ..feeds import ashby_internships_us

COMPANY_NAME = "Parallel"
CAREERS_URL = "https://jobs.ashbyhq.com/parallel"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("parallel")
