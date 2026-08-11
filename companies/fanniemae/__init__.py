from ..feeds import workday_internships_us

COMPANY_NAME = "Fannie Mae"
CAREERS_URL = "https://www.fanniemae.com/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("fanniemae", "FannieMaeCareers", host="wd1")
