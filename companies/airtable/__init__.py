from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Airtable"
CAREERS_URL = "https://job-boards.greenhouse.io/airtable"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("airtable")
