from ..feeds import greenhouse_internships_us

COMPANY_NAME = "HubSpot"
CAREERS_URL = "https://www.hubspot.com/careers/jobs"


def fetch_jobs() -> list[dict]:
    # HubSpot's live Greenhouse board token is "hubspotjobs"; the bare
    # "hubspot" token resolves but is empty.
    return greenhouse_internships_us("hubspotjobs")
