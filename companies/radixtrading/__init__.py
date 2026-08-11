from ...filters import is_internship_title, is_swe_ml_title, is_us_location
from ..feeds import greenhouse_jobs

COMPANY_NAME = "Radix Trading"
CAREERS_URL = "https://radixtrading.co/"

# Radix's board lists bare city names; its only offices are Chicago,
# New York, and Amsterdam.
_US_OFFICES = {"chicago", "new york"}


def fetch_jobs() -> list[dict]:
    # Radix splits boards: "radixuniversity" carries internships and campus
    # roles; "radixexperienced" is experienced-only.
    return greenhouse_jobs("radixuniversity")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    # Radix titles its software internships "Quantitative Technologist
    # (C++ Intern)", which the generic SWE/ML title filter rejects — accept
    # Technologist internships alongside conventionally titled SWE ones.
    return [
        job for job in jobs
        if is_internship_title(job["title"])
        and (is_swe_ml_title(job["title"]) or "technologist" in job["title"].lower())
        and any(
            location.strip().lower() in _US_OFFICES or is_us_location(location)
            for location in job["locations"]
        )
    ]
