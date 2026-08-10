from ..feeds import ashby_internships_us

COMPANY_NAME = "Numeral"
CAREERS_URL = "https://jobs.ashbyhq.com/numeral"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("numeral")
