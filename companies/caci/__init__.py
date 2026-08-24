from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "CACI International"
CAREERS_URL = "https://careers.caci.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "caci", "External", host="wd1", title_filter=role_title_filter()
    )
