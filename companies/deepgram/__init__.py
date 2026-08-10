from ..feeds import ashby_internships_us

COMPANY_NAME = "Deepgram"
CAREERS_URL = "https://jobs.ashbyhq.com/deepgram"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("deepgram")
