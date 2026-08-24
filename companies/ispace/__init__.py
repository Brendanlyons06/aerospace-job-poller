from ...profiles import role_title_filter
from ..feeds import lever_internships_us

COMPANY_NAME = "ispace"
CAREERS_URL = "https://ispace-us.com/career/"


def fetch_jobs() -> list[dict]:
    return lever_internships_us(
        "ispace-inc",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
