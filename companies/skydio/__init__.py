from ...profiles import role_title_filter
from ..feeds import ashby_internships_us

COMPANY_NAME = "Skydio"
CAREERS_URL = "https://jobs.ashbyhq.com/skydio"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us(
        "skydio", title_filter=role_title_filter()
    )
