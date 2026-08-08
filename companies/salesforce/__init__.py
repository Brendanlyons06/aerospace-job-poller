from ..feeds import technical_internships, workday_jobs

COMPANY_NAME = "Salesforce"
CAREERS_URL = "https://careers.salesforce.com/en/jobs/"


def fetch_jobs() -> list[dict]:
    return workday_jobs("salesforce", "External_Career_Site", host="wd12")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
