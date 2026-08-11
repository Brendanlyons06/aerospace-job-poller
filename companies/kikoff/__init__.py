from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Kikoff"
CAREERS_URL = "https://kikoff.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("kikoff")
