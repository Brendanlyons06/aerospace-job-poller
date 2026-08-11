from ..feeds import workday_internships_us

COMPANY_NAME = "PayPal"
CAREERS_URL = "https://careers.pypl.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("paypal", "jobs", host="wd1")
