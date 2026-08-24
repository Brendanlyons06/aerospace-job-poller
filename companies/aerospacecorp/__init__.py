from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "The Aerospace Corporation"
CAREERS_URL = "https://aerospace.org/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "aero", "external", title_filter=role_title_filter()
    )
