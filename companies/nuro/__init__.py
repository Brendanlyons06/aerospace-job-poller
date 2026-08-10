from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Nuro"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("nuro")
