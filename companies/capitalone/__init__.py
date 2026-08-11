from ..feeds import workday_internships_us

COMPANY_NAME = "Capital One"
CAREERS_URL = "https://www.capitalonecareers.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("capitalone", "Capital_One", host="wd12")
