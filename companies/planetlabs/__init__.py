from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Planet Labs"
CAREERS_URL = "https://www.planet.com/company/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "planetlabs", title_filter=role_title_filter(include_generic_engineering=True)
    )
