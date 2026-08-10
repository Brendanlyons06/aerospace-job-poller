"""Small read-only feed helpers used by company-specific adapters.

Each adapter still owns its official careers URL, board identifier, and
filter. These helpers only normalize the public JSON shape returned by the
careers sites' own listing feeds.
"""

import html
import json
import re
from urllib.parse import unquote, urljoin

from curl_cffi import requests

from .. import http
from ..filters import internships_in_us, is_internship_title, is_us_location


def _embedded_json(page: str, marker: str):
    """Decode the JSON value immediately following a unique page marker."""
    start = page.find(marker)
    if start < 0:
        raise ValueError(f"could not find {marker!r} in careers page")
    return json.JSONDecoder().raw_decode(page, start + len(marker))[0]


def official_page_jobs(
    careers_url: str,
    link_pattern: str,
    *,
    listing_url: str | None = None,
) -> list[dict]:
    """Extract jobs rendered directly by a company's official careers page.

    ``link_pattern`` must contain one capture group for the stable job ID.
    This deliberately reads the company page, rather than an ATS vendor's
    listing API.  ``listing_url`` is useful where the official page links out
    to the ATS only for the application form: alerts should still take the
    user back to the company's own careers site.
    """
    with http.session() as session:
        response = session.get(careers_url)
        response.raise_for_status()
        page = response.text

    anchor = re.compile(
        r'<a\b[^>]*\bhref=["\'](?P<href>[^"\']+)["\'][^>]*>'
        r'(?P<body>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    pattern = re.compile(link_pattern, re.IGNORECASE)
    jobs = []
    seen = set()
    for match in anchor.finditer(page):
        href = html.unescape(match.group("href")).replace("\\u0026", "&")
        id_match = pattern.search(href)
        if not id_match:
            continue
        job_id = id_match.group(1)
        if job_id in seen:
            continue
        title = re.sub(r"<[^>]+>", " ", match.group("body"))
        title = re.sub(r"\s+", " ", html.unescape(title)).strip()
        # Inline CSS occasionally appears before the visible anchor text.
        title = re.sub(r"(?:\.[\w-]+\s*\{[^{}]*\}\s*)+", "", title).strip()
        if not title:
            continue
        seen.add(job_id)
        jobs.append(
            {
                "id": str(job_id),
                "title": title,
                "locations": [],
                "url": listing_url or urljoin(careers_url, href),
            }
        )
    return jobs


def greenhouse_jobs(board: str, *, content: bool = False) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    if content:
        url += "?content=true"
    payload = http.get_json(url)
    jobs = []
    for job in payload.get("jobs", []):
        location = (job.get("location") or {}).get("name")
        locations = [location] if location else []
        for metadata in (job.get("metadata") or []):
            if metadata.get("name") in {"Job Posting Location", "Location"}:
                value = metadata.get("value")
                if isinstance(value, list):
                    locations.extend(v for v in value if isinstance(v, str))
                elif isinstance(value, str):
                    locations.append(value)
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": list(dict.fromkeys(locations)),
                "url": job["absolute_url"],
            }
        )
    return jobs


def _greenhouse_page_jobs(payload: dict) -> list[dict]:
    jobs = []
    for job in payload.get("data", []):
        location = job.get("location")
        locations = []
        if isinstance(location, str):
            locations = [part.strip() for part in location.split(";") if part.strip()]
        if job.get("id") and job.get("title") and job.get("absolute_url"):
            jobs.append(
                {
                    "id": str(job["id"]),
                    "title": job["title"],
                    "locations": locations,
                    "url": job["absolute_url"],
                }
            )
    return jobs


def _greenhouse_us_office_ids(board: str) -> list[int]:
    """Resolve the live office IDs represented by the hosted Location filter."""
    payload = http.get_json(
        f"https://boards-api.greenhouse.io/v1/boards/{board}/offices"
    )
    offices = payload.get("offices", [])
    by_id = {office.get("id"): office for office in offices}

    def is_us_office(office: dict) -> bool:
        current = office
        visited = set()
        while current and current.get("id") not in visited:
            visited.add(current.get("id"))
            if is_us_location(current.get("location") or current.get("name") or ""):
                return True
            current = by_id.get(current.get("parent_id"))
        return False

    return [office["id"] for office in offices if office.get("id") and is_us_office(office)]


def greenhouse_internships_us(board: str) -> list[dict]:
    """Use Greenhouse's hosted internship and Location filters when available.

    The modern Greenhouse board submits ``field_<id>[]`` and ``offices[]``
    query parameters to its own route loader. Boards without an internship
    custom field expose only keyword search, so those use the site's
    ``keyword=intern`` request followed by strict title validation. If a
    company disables the hosted route, the public feed is the documented
    fallback and both constraints are validated locally.
    """
    board_url = f"https://job-boards.greenhouse.io/{board}"
    try:
        with http.session() as session:
            response = session.get(board_url)
            response.raise_for_status()
            page = response.text

            custom_fields = _embedded_json(page, '"customFields":')
            internship_options = []
            for field in custom_fields:
                for option in field.get("options", []):
                    if is_internship_title(option.get("name", "")):
                        internship_options.append((field.get("id"), option.get("id")))

            params: list[tuple[str, str | int]] = []
            exact_job_type = bool(internship_options)
            if exact_job_type:
                for field_id, option_id in internship_options:
                    if field_id and option_id:
                        params.append((f"field_{field_id}[]", option_id))
            else:
                params.append(("keyword", "intern"))

            us_office_ids = _greenhouse_us_office_ids(board)
            params.extend(("offices[]", office_id) for office_id in us_office_ids)

            jobs = []
            page_number = 1
            while True:
                page_params = [*params, ("page", page_number)]
                response = session.get(board_url, params=page_params)
                response.raise_for_status()
                job_posts = _embedded_json(response.text, '"jobPosts":')
                jobs.extend(_greenhouse_page_jobs(job_posts))
                if page_number >= int(job_posts.get("total_pages") or 1):
                    break
                page_number += 1

        if not exact_job_type:
            jobs = [job for job in jobs if is_internship_title(job["title"])]
        if not us_office_ids:
            jobs = [job for job in jobs if any(is_us_location(loc) for loc in job["locations"])]
        else:
            for job in jobs:
                job["locations"] = [
                    location
                    if is_us_location(location)
                    else f"{location}, United States"
                    for location in job["locations"]
                ]
        return list({job["id"]: job for job in jobs}.values())
    except (
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        requests.exceptions.RequestException,
    ):
        return internships_in_us(greenhouse_jobs(board, content=True))


def workday_jobs(
    tenant: str,
    site: str,
    *,
    search_text: str = "intern",
    host: str = "wd5",
    applied_facets: dict | None = None,
) -> list[dict]:
    """Read the public Workday search feed used by an official careers site."""
    endpoint = (
        f"https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/"
        f"{tenant}/{site}/jobs"
    )
    detail_base = f"https://{tenant}.{host}.myworkdayjobs.com/en-US/{site}"
    jobs = []
    offset = 0
    page_size = 20
    with http.session() as session:
        while True:
            response = session.post(
                endpoint,
                json={
                    "appliedFacets": applied_facets or {},
                    "limit": page_size,
                    "offset": offset,
                    "searchText": search_text,
                },
            )
            response.raise_for_status()
            payload = response.json()
            postings = payload.get("jobPostings", [])
            for posting in postings:
                job_id = (posting.get("bulletFields") or [None])[0]
                path = posting.get("externalPath")
                if not job_id or not path:
                    continue
                location = posting.get("locationsText")
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": posting.get("title", ""),
                        "locations": [location] if location else [],
                        "url": detail_base + path,
                    }
                )
            offset += len(postings)
            if not postings or len(postings) < page_size or offset >= payload.get("total", 0):
                break
    return jobs


def _workday_facets(facets: list[dict]):
    """Yield nested Workday facet groups as ``(parameter, values)`` pairs."""
    for facet in facets:
        values = facet.get("values") or []
        if values and all("id" in value for value in values):
            yield facet.get("facetParameter"), values, facet.get("descriptor")
        for value in values:
            if isinstance(value, dict) and value.get("values"):
                yield from _workday_facets([value])


def workday_internships_us(
    tenant: str,
    site: str,
    *,
    host: str = "wd5",
) -> list[dict]:
    """Discover and apply a Workday site's live Job Type and U.S. facets."""
    endpoint = (
        f"https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/"
        f"{tenant}/{site}/jobs"
    )
    with http.session() as session:
        response = session.post(
            endpoint,
            json={"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""},
        )
        response.raise_for_status()
        groups = list(_workday_facets(response.json().get("facets", [])))

    applied: dict[str, list[str]] = {}
    for parameter, values, descriptor in groups:
        if parameter and (descriptor or "").lower() == "job type":
            ids = [
                value["id"] for value in values
                if is_internship_title(value.get("descriptor", ""))
            ]
            if ids:
                applied[parameter] = ids
                break

    # Prefer a single country-level facet. If the site only exposes offices,
    # submit all U.S. office values (OR semantics within a Workday facet).
    for parameter, values, descriptor in groups:
        if not parameter:
            continue
        exact_country = [
            value["id"] for value in values
            if re.fullmatch(
                r"(?:United States(?: of America)?|US|USA)",
                value.get("descriptor", ""),
                re.IGNORECASE,
            )
        ]
        if exact_country:
            applied[parameter] = exact_country
            break
    else:
        for parameter, values, _descriptor in groups:
            if not parameter:
                continue
            ids = [
                value["id"] for value in values
                if is_us_location(value.get("descriptor", ""))
            ]
            if ids:
                applied[parameter] = ids
                break

    if not applied:
        return internships_in_us(
            workday_jobs(tenant, site, host=host, search_text="intern")
        )
    jobs = workday_jobs(
        tenant,
        site,
        host=host,
        search_text="",
        applied_facets=applied,
    )
    # A missing type or country facet is unusual but possible in customized
    # tenants; enforce only the constraint Workday could not represent.
    has_type = any(
        parameter in applied and (descriptor or "").lower() == "job type"
        for parameter, _values, descriptor in groups
    )
    has_country = any(
        parameter in applied and (descriptor or "").lower() != "job type"
        for parameter, _values, descriptor in groups
    )
    if not has_type:
        jobs = [job for job in jobs if is_internship_title(job["title"])]
    if not has_country:
        jobs = [job for job in jobs if any(is_us_location(loc) for loc in job["locations"])]
    else:
        for job in jobs:
            job["locations"] = [
                location
                if is_us_location(location)
                else f"{location}, United States"
                for location in job["locations"]
            ]
    return jobs


def amazon_jobs() -> list[dict]:
    """Use Amazon's official keyword and country filters for U.S. internships."""
    jobs = []
    offset = 0
    page_size = 100
    while True:
        payload = http.get_json(
            "https://www.amazon.jobs/en/search.json",
            params={
                "base_query": "intern",
                "country": "USA",
                "offset": offset,
                "result_limit": page_size,
            },
        )
        page = payload.get("jobs", [])
        for job in page:
            if job.get("country_code") not in {None, "US", "USA"}:
                continue
            if not is_internship_title(job.get("title", "")):
                continue
            locations = job.get("locations")
            if isinstance(locations, str):
                locations = [locations]
            elif not isinstance(locations, list):
                locations = []
            normalized_locations = []
            for location in locations:
                try:
                    data = json.loads(location) if isinstance(location, str) else location
                except json.JSONDecodeError:
                    data = None
                if isinstance(data, dict):
                    if data.get("countryIso2a") == "US" or data.get("countryIso3a") == "USA":
                        normalized_locations.append(
                            data.get("normalizedLocation") or data.get("location")
                        )
                elif isinstance(location, str):
                    normalized_locations.append(location)
            locations = [location for location in normalized_locations if location]
            if not locations:
                city = ", ".join(
                    value for value in (job.get("city"), job.get("state")) if value
                )
                if city:
                    locations = [city]
            path = job.get("job_path") or job.get("job_url")
            url = path if isinstance(path, str) and path.startswith("http") else (
                "https://www.amazon.jobs" + path if path else None
            )
            if job.get("id") and job.get("title") and url:
                jobs.append(
                    {
                        "id": str(job["id"]),
                        "title": job["title"],
                        "locations": locations,
                        "url": url,
                    }
                )
        offset += len(page)
        if not page or len(page) < page_size:
            break
    return jobs


def databricks_jobs() -> list[dict]:
    """Read Databricks' official job-detail sitemap.

    The careers page renders the same detail URLs client-side. The official
    sitemap is a smaller, stable feed of those pages and avoids depending on
    the ATS that powers the site's backend.
    """
    sitemap_url = "https://www.databricks.com/careers-assets/sitemap/sitemap-0.xml"
    with http.session() as session:
        response = session.get(sitemap_url)
        response.raise_for_status()
        urls = re.findall(
            r"<loc>(https://www\.databricks\.com/company/careers/[^<]+)</loc>",
            response.text,
        )
    jobs = []
    seen = set()
    for url in urls:
        path = url.rstrip("/").rsplit("/", 1)[-1]
        match = re.search(r"-(\d{10})$", path)
        if not match or match.group(1) in seen:
            continue
        seen.add(match.group(1))
        title_slug = path[: match.start()]
        title = re.sub(r"-+", " ", unquote(title_slug)).strip().title()
        jobs.append(
            {
                "id": match.group(1),
                "title": title,
                "locations": [],
                "url": url,
            }
        )
    return jobs


def anthropic_jobs() -> list[dict]:
    """Read the listings rendered on Anthropic's official jobs page."""
    careers_url = "https://www.anthropic.com/careers/jobs"
    with http.session() as session:
        response = session.get(careers_url)
        response.raise_for_status()
        text = response.text
    jobs = []
    pattern = re.compile(
        r'<a href="(https://[^"/]+/anthropic/jobs/(\d+))"[^>]*>'
        r'(.*?)</a>',
        re.S,
    )
    for match in pattern.finditer(text):
        card = match.group(3)
        role = re.search(r"jobRole[^>]*>.*?<p[^>]*>(.*?)</p>", card, re.S)
        location = re.search(r"jobLocation[^>]*>.*?<p[^>]*>(.*?)</p>", card, re.S)
        if not role:
            continue
        clean = lambda value: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()
        jobs.append(
            {
                "id": match.group(2),
                "title": clean(role.group(1)),
                "locations": [clean(location.group(1))] if location else [],
                "url": match.group(1),
            }
        )
    return jobs


def ibm_jobs() -> list[dict]:
    """Read the internship search feed used by IBM Careers."""
    endpoint = "https://www-api.ibm.com/search/api/v1/ibmcom/appid/careers/agg"
    jobs = []
    seen = set()
    page = 1
    with http.session() as session:
        while True:
            response = session.get(
                endpoint,
                params=[
                    ("scope", "careers2"),
                    ("rmdt", "ALL"),
                    ("appid", "careers"),
                    ("sortby", "pageviews_desc"),
                    ("query", "intern"),
                    ("lang", "en"),
                    ("fr", 0),
                    ("nr", 30),
                    ("page", page),
                    ("filter", "field_keyword_18:Internship"),
                    ("filter", 'field_keyword_05:"United States"'),
                ],
            )
            response.raise_for_status()
            search = response.json().get("resultset", {}).get("searchresults", {})
            results = search.get("searchresultlist", [])
            for result in results:
                url = result.get("url")
                if not isinstance(url, str) or "careers.ibm.com/" not in url:
                    continue
                attributes = {
                    key: value
                    for attribute in result.get("docattributes", [])
                    for key, value in attribute.items()
                }
                job_id = attributes.get("field_text_01")
                if not job_id:
                    match = re.search(r"[?&]jobId=([^&]+)", url)
                    job_id = match.group(1) if match else result.get("id")
                if not job_id or str(job_id) in seen:
                    continue
                seen.add(str(job_id))
                location = attributes.get("field_keyword_19")
                if attributes.get("field_keyword_05") != "United States":
                    continue
                if location and not is_us_location(location):
                    location = f"{location}, United States"
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": result.get("title", ""),
                        "locations": [location] if location else [],
                        "url": url,
                    }
                )

            total = int(search.get("totalresults") or 0)
            returned = int(search.get("numresults") or len(results))
            if not results or page >= (total + max(returned, 1) - 1) // max(returned, 1):
                break
            page += 1
    return jobs


def palantir_jobs() -> list[dict]:
    """Read Palantir's own API using its exact Lever employment category."""
    endpoint = "https://www.palantir.com/api/lever/v1/postings?state=published"
    jobs = []
    seen = set()
    cursor = None
    with http.session() as session:
        while True:
            url = endpoint if cursor is None else f"{endpoint}&offset={cursor}"
            response = session.get(url)
            response.raise_for_status()
            payload = response.json()
            for posting in payload.get("data", []):
                job_id = posting.get("id")
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)
                categories = posting.get("categories") or {}
                if categories.get("commitment") != "Intern":
                    continue
                location = categories.get("location")
                locations = categories.get("allLocations") or (
                    [location] if location else []
                )
                urls = posting.get("urls") or {}
                url = urls.get("show") or "https://www.palantir.com/careers/open-positions/"
                normalized = {
                    "id": str(job_id),
                    "title": posting.get("text", ""),
                    "locations": locations,
                    "url": url,
                }
                if any(is_us_location(item) for item in locations):
                    jobs.append(normalized)
            if not payload.get("hasNext") or not payload.get("next"):
                break
            cursor = payload["next"]
    return jobs


def google_jobs() -> list[dict]:
    """Read the result records embedded in Google Careers' official search page."""
    url = (
        "https://www.google.com/about/careers/applications/jobs/results/"
        "?q=intern&location=United%20States"
    )
    with http.session() as session:
        response = session.get(url)
        response.raise_for_status()
        text = response.text
    marker = "AF_initDataCallback({key: 'ds:1'"
    start = text.find(marker)
    if start < 0:
        raise ValueError("Google Careers result data was not present")
    data_start = text.find("data:", start) + len("data:")
    data_end = text.find(", sideChannel:", data_start)
    if data_start < len("data:") or data_end < 0:
        raise ValueError("Google Careers result data was malformed")
    rows = json.loads(text[data_start:data_end])[0]
    detail_links = {
        title: "https://www.google.com/about/careers/applications/" + path
        for path, title in re.findall(
            r'href="(jobs/results/[^" ]+)"[^>]*aria-label="Learn more about ([^"]+)"',
            text,
        )
    }
    jobs = []
    for row in rows:
        if len(row) < 10 or not row[0] or not row[1]:
            continue
        locations = [location[0] for location in (row[9] or []) if location]
        jobs.append(
            {
                "id": str(row[0]),
                "title": row[1],
                "locations": locations,
                "url": detail_links.get(row[1], row[2]),
            }
        )
    return internships_in_us(jobs)


def google_technical_internships(jobs: list[dict]) -> list[dict]:
    """Google's Student Researcher postings are internship-style technical roles."""
    return [
        job
        for job in jobs
        if "student researcher" in job["title"].lower()
        or technical_internships([job])
    ]


def phenom_internships_us(careers_url: str) -> list[dict]:
    """Use Phenom's official internship search, validating its country field."""
    return internships_in_us(phenom_jobs(careers_url))


def phenom_jobs(careers_url: str) -> list[dict]:
    """Read the SSR JSON embedded in a Phenom-powered official careers page."""
    jobs = []
    seen = set()
    # Phenom defaults to ten results and relevance ordering can move jobs
    # between pages between two polls. Request a larger page so normal-sized
    # internship searches arrive in one deterministic response.
    page_size = 100
    with http.session() as session:
        first_page = None
        total_hits = None
        for offset in range(0, 1000, page_size):
            separator = "&" if "?" in careers_url else "?"
            # `size` is the Phenom page size. The similarly named `s`
            # parameter resets the keyword search on these boards, so leave
            # it out.
            url = f"{careers_url}{separator}from={offset}&size={page_size}"
            response = session.get(url)
            response.raise_for_status()
            match = re.search(r"phApp\.ddo\s*=\s*(\{.*?\});", response.text, re.S)
            if not match:
                raise ValueError(f"could not find embedded job data in {url}")
            data = json.loads(html.unescape(match.group(1)))
            search_data = data.get("eagerLoadRefineSearch", {}).get("data", {})
            page = search_data.get("jobs", [])
            if first_page is None:
                first_page = page
                # Phenom's aggregations repeat the total for the primary
                # facets. Pick the smallest facet total to avoid counting
                # multi-valued locations as separate jobs.
                totals = [
                    sum((agg.get("value") or {}).values())
                    for agg in (search_data.get("aggregations") or [])
                    if isinstance(agg.get("value"), dict)
                ]
                if totals:
                    total_hits = min(totals)
            for job in page:
                job_id = job.get("reqId") or job.get("jobId") or job.get("jobSeqNo")
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)
                locations = job.get("multi_location") or job.get("location") or []
                if isinstance(locations, str):
                    locations = [locations]
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": job.get("title", ""),
                        "locations": locations,
                        "url": job.get("applyUrl") or careers_url,
                    }
                )
            if not page or len(page) < page_size or (
                total_hits is not None and len(jobs) >= total_hits
            ):
                break
    return jobs


def ashby_jobs(board: str) -> list[dict]:
    payload = http.get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    jobs = []
    for job in payload.get("jobs", []):
        location = job.get("location")
        locations = [location] if isinstance(location, str) and location else []
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": locations,
                "url": job.get("jobUrl") or job.get("applyUrl"),
            }
        )
    return jobs


def _ashby_location_is_us(location: dict) -> bool:
    address = (location.get("address") or {}).get("postalAddress") or {}
    country = address.get("addressCountry")
    return country in {"US", "USA", "United States", "United States of America"}


def ashby_internships_us(board: str) -> list[dict]:
    """Mirror Ashby's UI filters using its exact structured posting fields.

    Ashby's public job-board UI filters the downloaded payload in the browser;
    the posting API does not accept filter parameters. ``employmentType`` and
    the structured primary/secondary country values are the same fields the
    first-party UI uses, and avoid guessing from title or free-form location.
    """
    payload = http.get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    jobs = []
    for job in payload.get("jobs", []):
        if job.get("employmentType") != "Intern":
            continue
        raw_locations = []
        primary = {
            "name": job.get("location"),
            "address": job.get("address"),
        }
        raw_locations.append(primary)
        raw_locations.extend(job.get("secondaryLocations") or [])
        us_locations = [
            location.get("name") or location.get("location")
            for location in raw_locations
            if isinstance(location, dict)
            and _ashby_location_is_us(location)
            and (location.get("name") or location.get("location"))
        ]
        if not us_locations:
            continue
        us_locations = [
            location if is_us_location(location) else f"{location}, United States"
            for location in us_locations
        ]
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": list(dict.fromkeys(us_locations)),
                "url": job.get("jobUrl") or job.get("applyUrl"),
            }
        )
    return jobs


def technical_internships(jobs: list[dict]) -> list[dict]:
    """Keep internship/co-op postings in software, ML, AI, or research."""
    import re

    technical = (
        "software", "engineering", "machine learning", "artificial intelligence",
        "research", "data science", "data engineer", "developer", "robotics",
    )
    internship = re.compile(r"\b(intern|internship|co-op|coop)\b", re.IGNORECASE)
    return [
        job
        for job in jobs
        if internship.search(job["title"])
        and (
            any(term in job["title"].lower() for term in technical)
            or re.search(r"\bai\b|\bml\b", job["title"], re.IGNORECASE)
        )
    ]
