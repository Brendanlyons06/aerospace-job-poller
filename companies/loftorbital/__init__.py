from ...profiles import role_title_filter
from ..feeds import lever_internships_us

COMPANY_NAME = "Loft Orbital"
CAREERS_URL = "https://www.loftorbital.com/careers"


def fetch_jobs() -> list[dict]:
    return lever_internships_us(
        "loftorbital",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
