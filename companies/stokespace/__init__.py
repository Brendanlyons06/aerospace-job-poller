from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Stoke Space"
CAREERS_URL = "https://www.stokespace.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "stokespacetechnologies", title_filter=role_title_filter()
    )
