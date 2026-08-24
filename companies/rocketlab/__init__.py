from ...profiles import role_title_filter
from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Rocket Lab"
CAREERS_URL = "https://rocketlabcorp.com/careers/positions/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us(
        "rocketlab", title_filter=role_title_filter()
    )
