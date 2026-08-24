from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "Leidos"
CAREERS_URL = "https://careers.leidos.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "leidos", "External", title_filter=role_title_filter()
    )
