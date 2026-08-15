from ..feeds import greenhouse_internships_us

COMPANY_NAME = "SeatGeek"
CAREERS_URL = "https://seatgeek.com/jobs"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("seatgeek")
