from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Tower Research Capital"
CAREERS_URL = "https://tower-research.com/open-positions/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("towerresearchcapital")
