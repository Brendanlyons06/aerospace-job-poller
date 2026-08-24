from ...profiles import role_title_filter
from ..feeds import clearcompany_internships_us

COMPANY_NAME = "Firefly Aerospace"
CAREERS_URL = "https://fireflyspace.com/careers/"


def fetch_jobs() -> list[dict]:
    return clearcompany_internships_us(
        "00ed92c3-5bfb-7bfb-456d-4d9d77fef9a5",
        title_filter=role_title_filter(),
    )
