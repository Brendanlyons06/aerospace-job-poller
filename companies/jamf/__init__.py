from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Jamf"
CAREERS_URL = "https://job-boards.greenhouse.io/jamf"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("jamf")
