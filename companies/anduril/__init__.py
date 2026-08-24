from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Anduril Industries"
CAREERS_URL = "https://job-boards.greenhouse.io/andurilindustries"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "andurilindustries", title_filter=role_title_filter()
    )
