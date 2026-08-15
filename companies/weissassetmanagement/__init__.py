from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Weiss Asset Management"
CAREERS_URL = "https://weissasset.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("weissassetmanagement")
