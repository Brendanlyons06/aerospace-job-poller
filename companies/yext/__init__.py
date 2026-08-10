from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Yext"
CAREERS_URL = "https://job-boards.greenhouse.io/yext"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("yext")
