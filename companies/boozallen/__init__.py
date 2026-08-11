from ..feeds import workday_internships_us

COMPANY_NAME = "Booz Allen Hamilton"
CAREERS_URL = "https://careers.boozallen.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("bah", "bah_jobs", host="wd1")
