from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Chicago Trading Company"
CAREERS_URL = "https://www.chicagotrading.com/careers/"


def fetch_jobs() -> list[dict]:
    # CTC posts campus roles on a dedicated campus board.
    return greenhouse_internships_us("ctccampusboard")
