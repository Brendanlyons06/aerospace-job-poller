from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Relativity Space"
CAREERS_URL = "https://www.relativityspace.com/jobs"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "relativity", title_filter=role_title_filter(include_generic_engineering=True)
    )
