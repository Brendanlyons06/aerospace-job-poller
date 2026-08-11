from ..feeds import greenhouse_internships_us

COMPANY_NAME = "DRW"
CAREERS_URL = "https://www.drw.com/work-at-drw"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("drweng")
