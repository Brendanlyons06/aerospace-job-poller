from ..feeds import workday_internships_us

COMPANY_NAME = "GEICO"
CAREERS_URL = "https://careers.geico.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("geico", "External", host="wd1")
