from ..feeds import workday_internships_us

COMPANY_NAME = "DraftKings"
CAREERS_URL = "https://careers.draftkings.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("draftkings", "DraftKings", host="wd1")
