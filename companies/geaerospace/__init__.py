from ...profiles import role_title_filter
from ..feeds import phenom_internships_us

COMPANY_NAME = "GE Aerospace"
CAREERS_URL = "https://careers.geaerospace.com/global/en/search-results?keywords=intern"


def fetch_jobs() -> list[dict]:
    return phenom_internships_us(
        CAREERS_URL, title_filter=role_title_filter()
    )
