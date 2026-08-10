from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Rubrik"
CAREERS_URL = "https://job-boards.greenhouse.io/rubrik"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("rubrik")
