from ..feeds import workday_internships_us

COMPANY_NAME = "RTX"
CAREERS_URL = "https://careers.rtx.com/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("globalhr", "rec_rtx_ext_gateway")
