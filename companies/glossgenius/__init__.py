from ..feeds import greenhouse_internships_us

COMPANY_NAME = "GlossGenius"
CAREERS_URL = "https://www.glossgenius.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("glossgenius")
