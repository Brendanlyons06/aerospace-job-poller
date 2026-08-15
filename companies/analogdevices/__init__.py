from ..feeds import workday_internships_us

COMPANY_NAME = "Analog Devices"
CAREERS_URL = "https://www.analog.com/en/about-adi/careers.html"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("analogdevices", "External", host="wd1")
