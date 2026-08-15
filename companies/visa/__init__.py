from ..feeds import workday_internships_us

COMPANY_NAME = "Visa"
CAREERS_URL = "https://corporate.visa.com/en/careers.html"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("visa", "Visa", host="wd5")
