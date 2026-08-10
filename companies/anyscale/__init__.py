from ..feeds import ashby_internships_us

COMPANY_NAME = "Anyscale"
CAREERS_URL = "https://jobs.ashbyhq.com/anyscale"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("anyscale")
