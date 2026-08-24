from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "Moog"
CAREERS_URL = "https://www.moog.com/careers.html"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "moog",
        "MOOG_External_Career_Site",
        host="wd5",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
