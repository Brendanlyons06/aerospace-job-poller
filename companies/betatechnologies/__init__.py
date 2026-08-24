from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "BETA Technologies"
CAREERS_URL = "https://beta.team/careers"


def _title_filter(title: str) -> bool:
    return (
        role_title_filter(include_generic_engineering=True)(title)
        or title.strip().lower() == "beta internship"
    )


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "betatechnologiesinc", title_filter=_title_filter
    )
