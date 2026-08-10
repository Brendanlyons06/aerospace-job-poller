from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Datadog"
CAREERS_URL = "https://careers.datadoghq.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("datadog")
