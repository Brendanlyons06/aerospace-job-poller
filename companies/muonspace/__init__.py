from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Muon Space"
CAREERS_URL = "https://www.muonspace.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "muonspace", title_filter=role_title_filter(include_generic_engineering=True)
    )
