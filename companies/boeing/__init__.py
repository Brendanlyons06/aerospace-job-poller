from ...profiles import role_title_filter
from ..feeds import talentbrew_internships_us

COMPANY_NAME = "Boeing"
CAREERS_URL = "https://jobs.boeing.com/internships"


def fetch_jobs() -> list[dict]:
    return talentbrew_internships_us(
        "https://jobs.boeing.com/en/category/internship-jobs/185/9287/1",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
