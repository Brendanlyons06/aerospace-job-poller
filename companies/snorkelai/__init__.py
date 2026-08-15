from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Snorkel AI"
CAREERS_URL = "https://snorkel.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("snorkelai")
