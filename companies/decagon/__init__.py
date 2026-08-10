from ..feeds import ashby_internships_us

COMPANY_NAME = "Decagon"
CAREERS_URL = "https://jobs.ashbyhq.com/decagon"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("decagon")
