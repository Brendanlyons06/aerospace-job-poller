from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Eikon Therapeutics"
CAREERS_URL = "https://www.eikontx.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("eikontherapeutics")
