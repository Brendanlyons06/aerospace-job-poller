from ..feeds import ashby_internships_us

COMPANY_NAME = "ElevenLabs"
CAREERS_URL = "https://jobs.ashbyhq.com/elevenlabs"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("elevenlabs")
