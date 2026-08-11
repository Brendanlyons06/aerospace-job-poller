from ..feeds import workday_internships_us

COMPANY_NAME = "Travelers"
CAREERS_URL = "https://careers.travelers.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("travelers", "External")
