from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Cribl"
CAREERS_URL = "https://job-boards.greenhouse.io/cribl"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("cribl")
