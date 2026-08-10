from ..feeds import greenhouse_internships_us

COMPANY_NAME = "BILL"
CAREERS_URL = "https://job-boards.greenhouse.io/billcom"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("billcom")
