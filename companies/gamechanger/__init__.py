from ..feeds import ashby_internships_us

COMPANY_NAME = "GameChanger"
CAREERS_URL = "https://gc.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("gamechanger")
