from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Cloudflare"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("cloudflare")
