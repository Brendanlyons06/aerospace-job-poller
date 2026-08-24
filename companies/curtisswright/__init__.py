from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "Curtiss-Wright"
CAREERS_URL = "https://www.curtisswright.com/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "curtisswright",
        "CW_External_Career_Site",
        host="wd1",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
