from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Viam"
CAREERS_URL = "https://www.viam.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("viamrobotics")
