from ..feeds import workday_internships_us

COMPANY_NAME = "Micron"
CAREERS_URL = "https://careers.micron.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("micron", "External", host="wd1")
