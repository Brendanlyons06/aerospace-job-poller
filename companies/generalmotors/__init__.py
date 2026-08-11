from ..feeds import workday_internships_us

COMPANY_NAME = "General Motors"
CAREERS_URL = "https://search-careers.gm.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("generalmotors", "Careers_GM")
