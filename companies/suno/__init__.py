from ..feeds import ashby_internships_us

COMPANY_NAME = "Suno"
CAREERS_URL = "https://jobs.ashbyhq.com/suno"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("suno")
