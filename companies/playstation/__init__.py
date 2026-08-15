from ..feeds import greenhouse_internships_us

COMPANY_NAME = "PlayStation"
CAREERS_URL = "https://www.playstation.com/en-us/corporate/playstation-careers/"


def fetch_jobs() -> list[dict]:
    # PlayStation's Greenhouse board token is "sonyinteractiveentertainmentglobal".
    return greenhouse_internships_us("sonyinteractiveentertainmentglobal")
