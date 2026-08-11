from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Samsung Semiconductor"
CAREERS_URL = "https://semiconductor.samsung.com/us/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("samsungsemiconductor")
