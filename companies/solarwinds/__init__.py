from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "SolarWinds"
CAREERS_URL = "https://job-boards.greenhouse.io/solarwinds"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("solarwinds")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
