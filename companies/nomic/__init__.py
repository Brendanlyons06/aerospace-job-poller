from ..feeds import ashby_internships_us

COMPANY_NAME = "Nomic"
CAREERS_URL = "https://jobs.ashbyhq.com/nomic"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("nomic")
