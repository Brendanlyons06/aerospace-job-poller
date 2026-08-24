from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Zipline"
CAREERS_URL = "https://www.flyzipline.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "flyzipline", title_filter=role_title_filter()
    )
