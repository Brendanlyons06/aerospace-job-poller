from ..feeds import workday_internships_us

COMPANY_NAME = "GE Appliances"
CAREERS_URL = "https://careers.geappliances.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("haier", "GE_Appliances", host="wd3")
