from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Optiver"
CAREERS_URL = "https://optiver.com/working-at-optiver/career-opportunities/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("optiverus")
