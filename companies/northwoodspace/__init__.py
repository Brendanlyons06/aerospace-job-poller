from ...profiles import role_title_filter
from ..feeds import ashby_internships_us

COMPANY_NAME = "Northwood Space"
CAREERS_URL = "https://www.northwoodspace.io/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us(
        "NorthwoodSpace",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
