from ..feeds import greenhouse_internships_us

COMPANY_NAME = "SolarWinds"
CAREERS_URL = "https://job-boards.greenhouse.io/solarwinds"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("solarwinds")
