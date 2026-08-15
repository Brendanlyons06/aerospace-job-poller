from ..feeds import ashby_internships_us

COMPANY_NAME = "Also"
CAREERS_URL = "https://www.rideálso.com/"


def fetch_jobs() -> list[dict]:
    # Also (Rivian's micromobility spinoff) posts under the Ashby board "Ridealso".
    return ashby_internships_us("Ridealso")
