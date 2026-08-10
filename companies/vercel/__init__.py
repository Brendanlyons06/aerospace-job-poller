from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Vercel"
CAREERS_URL = "https://vercel.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("vercel")
