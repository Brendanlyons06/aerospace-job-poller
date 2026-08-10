from ..feeds import greenhouse_internships_us

COMPANY_NAME = "BitGo"
CAREERS_URL = "https://job-boards.greenhouse.io/bitgo"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("bitgo")
