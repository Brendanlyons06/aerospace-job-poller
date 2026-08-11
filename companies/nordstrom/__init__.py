from ..feeds import workday_internships_us

COMPANY_NAME = "Nordstrom"
CAREERS_URL = "https://careers.nordstrom.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("nordstrom", "nordstrom_careers", host="wd501")
