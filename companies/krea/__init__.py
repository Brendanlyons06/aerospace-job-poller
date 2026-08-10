from ..feeds import ashby_internships_us

COMPANY_NAME = "Krea"
CAREERS_URL = "https://jobs.ashbyhq.com/krea"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("krea")
