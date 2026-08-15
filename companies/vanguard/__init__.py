from ..feeds import workday_internships_us

COMPANY_NAME = "Vanguard"
CAREERS_URL = "https://www.vanguardjobs.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("vanguard", "vanguard_external")
