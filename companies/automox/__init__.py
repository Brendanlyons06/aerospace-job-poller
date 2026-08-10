from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Automox"
CAREERS_URL = "https://job-boards.greenhouse.io/automox"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("automox")
