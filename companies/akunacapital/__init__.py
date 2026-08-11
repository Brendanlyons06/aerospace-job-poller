from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Akuna Capital"
CAREERS_URL = "https://akunacapital.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("akunacapital")
