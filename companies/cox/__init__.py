from ..feeds import workday_internships_us

COMPANY_NAME = "Cox"
CAREERS_URL = "https://jobs.coxenterprises.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("cox", "Cox_External_Career_Site_1", host="wd1")
