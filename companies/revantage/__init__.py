from ..feeds import workday_internships_us

COMPANY_NAME = "Revantage"
CAREERS_URL = "https://www.revantage.com/careers/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("revantage", "Revantage", host="wd1")
