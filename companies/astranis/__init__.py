from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Astranis"
CAREERS_URL = "https://job-boards.greenhouse.io/astranis"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "astranis", title_filter=role_title_filter()
    )
