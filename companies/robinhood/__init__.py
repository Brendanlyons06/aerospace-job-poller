from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Robinhood"
CAREERS_URL = "https://job-boards.greenhouse.io/robinhood"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("robinhood")
