from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Vast"
CAREERS_URL = "https://www.vastspace.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "vast", title_filter=role_title_filter(include_generic_engineering=True)
    )
