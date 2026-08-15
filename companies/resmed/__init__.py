from ..feeds import workday_internships_us

COMPANY_NAME = "ResMed"
CAREERS_URL = "https://careers.resmed.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("resmed", "ResMed_External_Careers", host="wd3")
