from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Zscaler"
CAREERS_URL = "https://job-boards.greenhouse.io/zscaler"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("zscaler")
