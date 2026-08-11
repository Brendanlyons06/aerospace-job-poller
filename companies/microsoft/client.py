"""Microsoft Careers — an Eightfold-powered site with a public search API.

careers.microsoft.com's search lives on ``apply.careers.microsoft.com``,
Eightfold's newer ``pcsx`` API (not the older ``/api/apply/v2/jobs`` shape
that Netflix and Millennium use — the payload nests under ``data`` and the
position fields differ, hence this client instead of ``feeds.eightfold_jobs``).
Anonymous GETs work; ``location`` accepts a plain country name and is
enforced by the API itself. Position ``id`` is Eightfold's stable numeric
identifier.

The pre-2026 endpoint (``gcsservices.careers.microsoft.com``) is dead — its
TLS certificate no longer matches. Don't resurrect it.
"""

from ... import http

API_URL = "https://apply.careers.microsoft.com/api/pcsx/search"
JOB_URL = "https://apply.careers.microsoft.com/careers/job/{position_id}"

_PAGE_SIZE = 10  # the API caps page size regardless of `num`


def search_positions(query: str, location: str) -> list[dict]:
    """Every position matching the site's own query + location search."""
    jobs = []
    seen = set()
    start = 0
    with http.session() as session:
        while True:
            response = session.get(
                API_URL,
                params={
                    "domain": "microsoft.com",
                    "query": query,
                    "location": location,
                    "start": start,
                },
                headers={"accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json().get("data") or {}
            positions = data.get("positions") or []
            for position in positions:
                position_id = position.get("id")
                if not position_id or str(position_id) in seen:
                    continue
                seen.add(str(position_id))
                jobs.append(
                    {
                        "id": str(position_id),
                        "title": position.get("name", ""),
                        "locations": [
                            location_name
                            for location_name in position.get("locations") or []
                            if isinstance(location_name, str)
                        ],
                        "url": JOB_URL.format(position_id=position_id),
                    }
                )
            start += len(positions)
            if not positions or start >= int(data.get("count") or 0):
                break
    return jobs
