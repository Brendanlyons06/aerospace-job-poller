from ..feeds import ashby_internships_us

COMPANY_NAME = "Capchase"
CAREERS_URL = "https://jobs.ashbyhq.com/capchase"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("capchase")
