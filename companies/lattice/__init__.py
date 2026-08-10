from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Lattice"
CAREERS_URL = "https://job-boards.greenhouse.io/lattice"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("lattice")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
