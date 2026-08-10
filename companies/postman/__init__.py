from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Postman"
CAREERS_URL = "https://job-boards.greenhouse.io/postman"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("postman")
