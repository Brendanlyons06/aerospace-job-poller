from ...profiles import role_title_filter
from ..feeds import ashby_internships_us

COMPANY_NAME = "Apex"
CAREERS_URL = "https://www.apexspace.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us(
        "apex-technology-inc", title_filter=role_title_filter()
    )
