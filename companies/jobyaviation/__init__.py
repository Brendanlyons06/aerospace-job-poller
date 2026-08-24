from ...profiles import role_title_filter
from ..feeds import icims_internships_us

COMPANY_NAME = "Joby Aviation"
CAREERS_URL = "https://www.jobyaviation.com/careers"


def fetch_jobs() -> list[dict]:
    return icims_internships_us(
        "careers-jobyaviation.icims.com",
        title_filter=role_title_filter(),
    )
