from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Geneva Trading"
CAREERS_URL = "https://www.genevatrading.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("genevatrading")
