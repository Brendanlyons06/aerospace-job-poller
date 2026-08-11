from ..feeds import workday_internships_us

COMPANY_NAME = "PIMCO"
CAREERS_URL = "https://careers.pimco.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("pimco", "pimco-careers", host="wd1")
