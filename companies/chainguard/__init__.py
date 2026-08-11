from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Chainguard"
CAREERS_URL = "https://job-boards.greenhouse.io/chainguard"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("chainguard")
