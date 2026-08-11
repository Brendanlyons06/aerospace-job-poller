from ..feeds import workday_internships_us

COMPANY_NAME = "Northrop Grumman"
CAREERS_URL = "https://www.northropgrumman.com/jobs"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("ngc", "Northrop_Grumman_External_Site", host="wd1")
