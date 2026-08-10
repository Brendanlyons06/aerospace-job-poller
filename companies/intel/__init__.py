from ..feeds import workday_internships_us

COMPANY_NAME = "Intel"
CAREERS_URL = "https://jobs.intel.com/en/search-jobs/intern"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("intel", "External", host="wd1")
