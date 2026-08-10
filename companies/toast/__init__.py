from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Toast"
CAREERS_URL = "https://careers.toasttab.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("toast")
