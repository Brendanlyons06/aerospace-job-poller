from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Discord"
CAREERS_URL = "https://discord.com/jobs"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("discord")
