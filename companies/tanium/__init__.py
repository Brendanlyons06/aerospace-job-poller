from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Tanium"
CAREERS_URL = "https://job-boards.greenhouse.io/tanium"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("tanium")
