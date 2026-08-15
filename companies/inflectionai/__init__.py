from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Inflection AI"
CAREERS_URL = "https://inflection.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("inflectionai")
