from ..feeds import eightfold_internships_us

COMPANY_NAME = "Millennium"
CAREERS_URL = "https://www.mlp.com/careers/"


def fetch_jobs() -> list[dict]:
    return eightfold_internships_us("mlp.eightfold.ai", "mlp.com")
