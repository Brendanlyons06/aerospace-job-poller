from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Coinbase"
CAREERS_URL = "https://www.coinbase.com/careers/positions"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("coinbase")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
