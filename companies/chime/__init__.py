from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Chime"
CAREERS_URL = "https://job-boards.greenhouse.io/chime"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("chime")
