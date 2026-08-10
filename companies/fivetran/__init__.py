from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Fivetran"
CAREERS_URL = "https://job-boards.greenhouse.io/fivetran"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("fivetran")
