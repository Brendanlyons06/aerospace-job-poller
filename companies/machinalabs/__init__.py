from ...profiles import role_title_filter
from ..feeds import ashby_internships_us

COMPANY_NAME = "Machina Labs"
CAREERS_URL = "https://www.machinalabs.ai/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us(
        "machina-labs",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
