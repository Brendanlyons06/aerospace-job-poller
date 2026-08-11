from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Hudson River Trading"
CAREERS_URL = "https://www.hudsonrivertrading.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("wehrtyou")
