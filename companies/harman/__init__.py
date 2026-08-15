from ..feeds import workday_internships_us

COMPANY_NAME = "Harman"
CAREERS_URL = "https://jobs.harman.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("harman", "HARMAN", host="wd3")
