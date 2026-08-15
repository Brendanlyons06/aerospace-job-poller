from ..feeds import workday_internships_us

COMPANY_NAME = "Wells Fargo"
CAREERS_URL = "https://www.wellsfargojobs.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("wf", "WellsFargoJobs", host="wd1")
