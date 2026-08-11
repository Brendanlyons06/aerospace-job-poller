from ..feeds import lever_internships_us

COMPANY_NAME = "Belvedere Trading"
CAREERS_URL = "https://www.belvederetrading.com/careers"


def fetch_jobs() -> list[dict]:
    return lever_internships_us("belvederetrading")
