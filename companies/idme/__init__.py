from ..feeds import greenhouse_internships_us

COMPANY_NAME = "ID.me"
CAREERS_URL = "https://job-boards.greenhouse.io/idme"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("idme")
