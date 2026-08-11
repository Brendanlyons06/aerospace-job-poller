from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Neros"
CAREERS_URL = "https://job-boards.greenhouse.io/nerostechnologies"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("nerostechnologies")
