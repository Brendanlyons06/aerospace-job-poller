from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Vercel"
CAREERS_URL = "https://vercel.com/careers"

def fetch_jobs() -> list[dict]:
    return official_page_jobs(CAREERS_URL, r"/careers/[^/]*-(\d+)")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
