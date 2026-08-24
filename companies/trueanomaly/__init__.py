from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "True Anomaly"
CAREERS_URL = "https://job-boards.greenhouse.io/trueanomalyinc"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "trueanomalyinc", title_filter=role_title_filter()
    )
