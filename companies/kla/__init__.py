from ..feeds import workday_internships_us

COMPANY_NAME = "KLA"
CAREERS_URL = "https://www.kla.com/company/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("kla", "Search", host="wd1")
