from ..feeds import workday_internships_us

COMPANY_NAME = "BlackRock"
CAREERS_URL = "https://careers.blackrock.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("blackrock", "BlackRock_Professional", host="wd1")
