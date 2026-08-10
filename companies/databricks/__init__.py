from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Databricks"
CAREERS_URL = "https://www.databricks.com/company/careers/open-positions"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("databricks")
