from ..feeds import workday_internships_us

COMPANY_NAME = "Arrowstreet Capital"
CAREERS_URL = "https://arrowstreetcapital.wd5.myworkdayjobs.com/Arrowstreet"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("arrowstreetcapital", "Arrowstreet")
