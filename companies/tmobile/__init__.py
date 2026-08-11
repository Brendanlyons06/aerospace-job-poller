from ..feeds import workday_internships_us

COMPANY_NAME = "T-Mobile"
CAREERS_URL = "https://careers.t-mobile.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("tmobile", "External", host="wd1")
