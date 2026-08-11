from ..feeds import workday_internships_us

COMPANY_NAME = "CME Group"
CAREERS_URL = "https://www.cmegroup.com/careers.html"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("cmegroup", "cme_careers", host="wd1")
