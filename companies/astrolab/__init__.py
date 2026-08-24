from ...profiles import role_title_filter
from ..feeds import pinpoint_internships_us

COMPANY_NAME = "Astrolab"
CAREERS_URL = "https://astrolab.pinpointhq.com/"


def fetch_jobs() -> list[dict]:
    return pinpoint_internships_us(
        "astrolab.pinpointhq.com",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
