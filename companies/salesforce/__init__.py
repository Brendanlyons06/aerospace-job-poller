from ..feeds import workday_internships_us

COMPANY_NAME = "Salesforce"
CAREERS_URL = "https://careers.salesforce.com/en/jobs/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us(
        "salesforce", "External_Career_Site", host="wd12"
    )
