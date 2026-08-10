from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Warp"
CAREERS_URL = "https://jobs.ashbyhq.com/warp"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("warp")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
