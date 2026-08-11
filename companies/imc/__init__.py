from ...filters import internships_in_us
from ..feeds import greenhouse_jobs

COMPANY_NAME = "IMC Trading"
CAREERS_URL = "https://www.imc.com/us/careers"


def fetch_jobs() -> list[dict]:
    # The hosted Greenhouse office filter currently returns Amsterdam even
    # when only U.S. offices are selected. Validate the public feed's original
    # location strings locally so foreign-only postings cannot be relabeled.
    return internships_in_us(greenhouse_jobs("imc", content=True))
