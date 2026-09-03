from ...profiles import role_title_filter
from ..feeds import talentbrew_category_internships_us

COMPANY_NAME = "L3Harris Technologies"
CAREERS_URL = (
    "https://careers.l3harris.com/en/employment/"
    "united-states-co-op-intern-jobs/4832/62394/6252001/2/1"
)


def fetch_jobs() -> list[dict]:
    return talentbrew_category_internships_us(
        CAREERS_URL,
        title_filter=role_title_filter(include_generic_engineering=True),
    )
