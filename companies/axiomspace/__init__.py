from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "Axiom Space"
CAREERS_URL = "https://www.axiomspace.com/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "axiomspace",
        "External_Career_Site",
        host="wd5",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
