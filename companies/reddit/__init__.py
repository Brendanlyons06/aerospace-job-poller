from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Reddit"
CAREERS_URL = "https://www.redditinc.com/careers"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(
        CAREERS_URL, r"/jobs/(\d+)", listing_url=CAREERS_URL
    )

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
