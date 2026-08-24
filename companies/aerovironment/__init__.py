from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "AeroVironment"
CAREERS_URL = "https://www.avinc.com/careers/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "avav",
        "AVAV",
        host="wd1",
        title_filter=role_title_filter(),
    )
