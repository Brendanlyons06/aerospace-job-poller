from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Appian"
CAREERS_URL = "https://appian.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("appian")
