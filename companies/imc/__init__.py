from ..feeds import greenhouse_internships_us

COMPANY_NAME = "IMC Trading"
CAREERS_URL = "https://www.imc.com/us/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("imc")
