from ..feeds import palantir_jobs

COMPANY_NAME = "Palantir"
CAREERS_URL = "https://www.palantir.com/careers/open-positions/"


def fetch_jobs() -> list[dict]:
    return palantir_jobs()
