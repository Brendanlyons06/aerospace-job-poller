from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Lucid Software"
CAREERS_URL = "https://job-boards.greenhouse.io/lucidsoftware"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("lucidsoftware")
