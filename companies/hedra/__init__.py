from ..feeds import ashby_internships_us

COMPANY_NAME = "Hedra"
CAREERS_URL = "https://jobs.ashbyhq.com/hedra"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("hedra")
