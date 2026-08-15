from ..feeds import workday_internships_us

COMPANY_NAME = "The Walt Disney Company"
CAREERS_URL = "https://www.disneycareers.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("disney", "disneycareer")
