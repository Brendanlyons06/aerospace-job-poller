from ..feeds import workday_internships_us

COMPANY_NAME = "eBay"
CAREERS_URL = "https://careers.ebayinc.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("ebay", "apply")
