from ...profiles import role_title_filter
from ..feeds import workday_internships_us

COMPANY_NAME = "Applied Materials"
CAREERS_URL = "https://www.appliedmaterials.com/us/en/careers.html"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "amat",
        "External",
        host="wd1",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
