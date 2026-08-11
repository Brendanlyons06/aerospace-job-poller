"""Read Rippling's public careers search feed."""

import json
import re
from urllib.parse import urlencode, urljoin

from ... import http

CAREERS_URL = "https://www.rippling.com/careers/open-roles"
HITS_PER_PAGE = 1000

_NEXT_DATA_RE = re.compile(
    r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.*?)</script>',
    re.DOTALL,
)
_APP_SCRIPT_RE = re.compile(
    r'<script[^>]+src="([^"]*/_next/static/chunks/pages/_app-[^"]+\.js)"'
)
_ALGOLIA_CONFIG_RE = re.compile(
    r"\.env\.ALGOLIA_ENV;let [$\w]+="
    r'"(?P<application_id>[^"]+)";[$\w]+\.env\.ALGOLIA_ADMIN_API_KEY;'
    r'let [$\w]+="(?P<api_key>[^"]+)"'
)


def _search_config(session) -> tuple[str, str, str]:
    """Resolve the live index and public search-only credential."""
    response = session.get(CAREERS_URL)
    response.raise_for_status()
    page = response.text

    next_data_match = _NEXT_DATA_RE.search(page)
    app_script_match = _APP_SCRIPT_RE.search(page)
    if not next_data_match or not app_script_match:
        raise ValueError("Rippling careers search configuration was not present")

    next_data = json.loads(next_data_match.group(1))
    try:
        index_name = next_data["props"]["pageProps"]["data"]["algoliaIndexName"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Rippling careers index name was not present") from exc

    script_url = urljoin(CAREERS_URL, app_script_match.group(1))
    response = session.get(script_url)
    response.raise_for_status()
    algolia_match = _ALGOLIA_CONFIG_RE.search(response.text)
    if not algolia_match:
        raise ValueError("Rippling careers search credential was not present")

    return (
        index_name,
        algolia_match.group("application_id"),
        algolia_match.group("api_key"),
    )


def fetch_job_hits() -> list[dict]:
    """Return every Algolia row matching Rippling's internship search.

    Rippling indexes a multi-location job once per location. The company
    adapter groups these rows by ``jobId`` before returning normalized jobs.
    """
    with http.session() as session:
        index_name, application_id, api_key = _search_config(session)
        endpoint = (
            f"https://{application_id}-dsn.algolia.net/1/indexes/*/queries"
        )
        headers = {
            "X-Algolia-Application-Id": application_id,
            "X-Algolia-API-Key": api_key,
            "Content-Type": "application/json",
        }

        hits = []
        page = 0
        while True:
            params = urlencode(
                {
                    "query": "intern",
                    "hitsPerPage": HITS_PER_PAGE,
                    "page": page,
                }
            )
            response = session.post(
                endpoint,
                headers=headers,
                json={"requests": [{"indexName": index_name, "params": params}]},
            )
            response.raise_for_status()
            payload = response.json()
            try:
                result = payload["results"][0]
                result_hits = result["hits"]
            except (KeyError, IndexError, TypeError) as exc:
                raise ValueError("Rippling careers search returned invalid data") from exc
            if not isinstance(result_hits, list):
                raise ValueError("Rippling careers search hits were not a list")
            hits.extend(result_hits)

            page += 1
            if page >= int(result.get("nbPages") or 1):
                break

    return hits
