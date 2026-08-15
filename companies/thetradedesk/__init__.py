from ..feeds import greenhouse_internships_us

COMPANY_NAME = "The Trade Desk"
CAREERS_URL = "https://careers.thetradedesk.com/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("thetradedesk")
