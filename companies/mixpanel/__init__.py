from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Mixpanel"
CAREERS_URL = "https://job-boards.greenhouse.io/mixpanel"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("mixpanel")
