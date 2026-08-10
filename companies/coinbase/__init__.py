from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Coinbase"
CAREERS_URL = "https://www.coinbase.com/careers/positions"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("coinbase")
