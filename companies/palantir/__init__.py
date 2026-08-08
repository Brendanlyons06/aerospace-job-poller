from ..feeds import palantir_jobs, technical_internships

COMPANY_NAME = "Palantir"
CAREERS_URL = "https://www.palantir.com/careers/open-positions/"


def fetch_jobs() -> list[dict]:
    return palantir_jobs()


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
