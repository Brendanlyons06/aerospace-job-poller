from ..feeds import workday_internships_us

COMPANY_NAME = "Workday"
CAREERS_URL = "https://workday.wd5.myworkdayjobs.com/Workday"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("workday", "Workday")
