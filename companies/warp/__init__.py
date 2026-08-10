from ..feeds import ashby_internships_us

COMPANY_NAME = "Warp"
CAREERS_URL = "https://jobs.ashbyhq.com/warp"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("warp")
