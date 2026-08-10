from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Attentive"
CAREERS_URL = "https://job-boards.greenhouse.io/attentive"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("attentive")
