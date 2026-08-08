from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "MongoDB"
CAREERS_URL = "https://www.mongodb.com/company/careers/see-jobs"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(CAREERS_URL, r"[?&]gh_jid=(\d+)", listing_url=CAREERS_URL)

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
