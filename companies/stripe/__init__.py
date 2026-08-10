import json

from ... import http
from ...filters import is_us_location

COMPANY_NAME = "Stripe"
CAREERS_URL = "https://stripe.com/careers/search"

def fetch_jobs() -> list[dict]:
    """Apply Stripe's exact Employment type and structured country fields."""
    with http.session() as session:
        response = session.get(CAREERS_URL)
        response.raise_for_status()
    page = response.text
    decoder = json.JSONDecoder()
    location_marker = '"locations":'
    listing_marker = '"listings":'
    location_start = page.find(location_marker)
    listing_start = page.find(listing_marker)
    if location_start < 0 or listing_start < 0:
        raise ValueError("Stripe careers data was not present")
    locations = decoder.raw_decode(page, location_start + len(location_marker))[0]
    listings = decoder.raw_decode(page, listing_start + len(listing_marker))[0]
    jobs = []
    for job in listings:
        if job.get("employmentType") != "Intern":
            continue
        us_locations = [
            locations[index]["name"]
            for index in job.get("locationIndices", [])
            if index < len(locations) and locations[index].get("countryCode") == "US"
        ]
        if not us_locations:
            continue
        us_locations = [
            location if is_us_location(location) else f"{location}, United States"
            for location in us_locations
        ]
        job_id = str(job["greenhouseId"])
        jobs.append(
            {
                "id": job_id,
                "title": job["title"],
                "locations": list(dict.fromkeys(us_locations)),
                "url": f"https://stripe.com/careers/listing/{job['slug']}/{job_id}",
            }
        )
    return jobs
