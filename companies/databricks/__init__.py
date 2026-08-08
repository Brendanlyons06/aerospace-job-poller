from ..feeds import databricks_jobs, technical_internships

COMPANY_NAME = "Databricks"
CAREERS_URL = "https://www.databricks.com/company/careers/open-positions"

def fetch_jobs() -> list[dict]:
    return databricks_jobs()

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
