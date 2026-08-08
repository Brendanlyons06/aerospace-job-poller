from ..feeds import technical_internships, workday_jobs

COMPANY_NAME = "NVIDIA"
CAREERS_URL = "https://www.nvidia.com/en-us/about-nvidia/careers/"


def fetch_jobs() -> list[dict]:
    return workday_jobs("nvidia", "NVIDIAExternalCareerSite")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
