from ..feeds import workday_internships_us

COMPANY_NAME = "Invesco"
CAREERS_URL = "https://careers.invesco.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("invesco", "IVZ", host="wd1")
