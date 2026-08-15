from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Calico Labs"
CAREERS_URL = "https://www.calicolabs.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("calicolabs")
