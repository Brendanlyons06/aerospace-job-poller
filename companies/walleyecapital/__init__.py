from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Walleye Capital"
CAREERS_URL = "https://walleyecapital.com/careers/"


def fetch_jobs() -> list[dict]:
    # Walleye posts campus roles on a separate students board; the main
    # "walleyecapital" board carries only experienced hires.
    return greenhouse_internships_us("walleyecapital-external-students")
