from ..feeds import workday_internships_us

COMPANY_NAME = "NVIDIA"
CAREERS_URL = "https://www.nvidia.com/en-us/about-nvidia/careers/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("nvidia", "NVIDIAExternalCareerSite")
