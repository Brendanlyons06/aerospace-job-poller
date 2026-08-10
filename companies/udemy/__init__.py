from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Udemy"
CAREERS_URL = "https://job-boards.greenhouse.io/udemy"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("udemy")
