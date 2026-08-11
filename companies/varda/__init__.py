from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Varda Space"
CAREERS_URL = "https://job-boards.greenhouse.io/vardaspace"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("vardaspace")
