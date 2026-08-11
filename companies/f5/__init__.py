from ..feeds import workday_internships_us

COMPANY_NAME = "F5"
CAREERS_URL = "https://www.f5.com/company/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("ffive", "f5jobs")
