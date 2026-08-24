from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Archer Aviation"
CAREERS_URL = "https://www.archer.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "archer56", title_filter=role_title_filter(include_generic_engineering=True)
    )
