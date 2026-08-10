from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Coupang"
CAREERS_URL = "https://job-boards.greenhouse.io/coupang"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("coupang")
