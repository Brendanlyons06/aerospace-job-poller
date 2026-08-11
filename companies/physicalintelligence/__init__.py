from ..feeds import ashby_internships_us

COMPANY_NAME = "Physical Intelligence"
CAREERS_URL = "https://www.physicalintelligence.company/"


def fetch_jobs() -> list[dict]:
    # An AI-research lab: its internship track is titled "Research
    # Internships", which the generic SWE/ML title check would drop — every
    # research role here is ML research, so keep all intern-typed postings.
    return ashby_internships_us("physicalintelligence", require_swe_ml=False)
