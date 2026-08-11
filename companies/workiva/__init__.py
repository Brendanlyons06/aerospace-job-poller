from ..feeds import workday_internships_us

COMPANY_NAME = "Workiva"
CAREERS_URL = "https://www.workiva.com/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("workiva", "careers", host="wd503")
