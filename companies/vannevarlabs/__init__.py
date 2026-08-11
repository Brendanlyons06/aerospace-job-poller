from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Vannevar Labs"
CAREERS_URL = "https://job-boards.greenhouse.io/vannevarlabs"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("vannevarlabs")
