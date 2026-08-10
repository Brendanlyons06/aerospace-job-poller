from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Anduril"
CAREERS_URL = "https://job-boards.greenhouse.io/andurilindustries"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("andurilindustries")
