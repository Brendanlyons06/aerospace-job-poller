from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Sumo Logic"
CAREERS_URL = "https://job-boards.greenhouse.io/sumologic"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("sumologic")
