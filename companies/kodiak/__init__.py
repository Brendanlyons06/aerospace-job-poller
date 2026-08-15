from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Kodiak Robotics"
CAREERS_URL = "https://kodiak.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("kodiak")
