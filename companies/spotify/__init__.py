from ...filters import internships_in_us
from ..feeds import lever_jobs

COMPANY_NAME = "Spotify"
CAREERS_URL = "https://www.lifeatspotify.com/jobs"


def fetch_jobs() -> list[dict]:
    # Spotify's Lever board doesn't use the "Intern" commitment category
    # (postings carry Permanent/Short Term), so validate internship + US
    # strictly from titles and locations instead.
    return internships_in_us(lever_jobs("spotify"))
