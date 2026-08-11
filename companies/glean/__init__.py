from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Glean"
CAREERS_URL = "https://www.glean.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("gleanwork")
