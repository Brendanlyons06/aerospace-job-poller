from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "Wisk Aero"
CAREERS_URL = "https://wisk.aero/careers/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "wisk",
        "Wisk_Careers",
        host="wd108",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
