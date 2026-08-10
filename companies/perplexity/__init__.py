from ..feeds import ashby_internships_us

COMPANY_NAME = "Perplexity"
CAREERS_URL = "https://www.perplexity.ai/hub/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("perplexity")
