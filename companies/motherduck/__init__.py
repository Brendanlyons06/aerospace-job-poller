from ..feeds import ashby_internships_us

COMPANY_NAME = "MotherDuck"
CAREERS_URL = "https://jobs.ashbyhq.com/motherduck"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("motherduck")
