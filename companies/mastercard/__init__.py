from ..feeds import workday_internships_us

COMPANY_NAME = "Mastercard"
CAREERS_URL = "https://careers.mastercard.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("mastercard", "CorporateCareers", host="wd1")
