from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Stripe"
CAREERS_URL = "https://stripe.com/careers/search"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(CAREERS_URL, r"/careers/listing/[^/]+/(\d+)")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
