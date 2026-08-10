from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Riot Games"
CAREERS_URL = "https://job-boards.greenhouse.io/riotgames"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("riotgames")
