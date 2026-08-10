from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Yext"
CAREERS_URL = "https://job-boards.greenhouse.io/yext"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("yext")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
