from ..feeds import workday_internships_us

COMPANY_NAME = "Expedia Group"
CAREERS_URL = "https://careers.expediagroup.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("expedia", "search", host="wd108")
