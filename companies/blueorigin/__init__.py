from ..feeds import workday_internships_us

COMPANY_NAME = "Blue Origin"
CAREERS_URL = "https://www.blueorigin.com/careers"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("blueorigin", "BlueOrigin")
