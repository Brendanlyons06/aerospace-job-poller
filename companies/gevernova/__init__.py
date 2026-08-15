from ..feeds import workday_internships_us

COMPANY_NAME = "GE Vernova"
CAREERS_URL = "https://careers.gevernova.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("gevernova", "Vernova_ExternalSite")
