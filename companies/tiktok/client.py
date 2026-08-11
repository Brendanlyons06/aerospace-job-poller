"""TikTok's lifeattiktok.com job-search API.

The public search endpoint accepts anonymous POSTs as long as the
``website-path: tiktok`` header is present (it scopes the portal; without it
the API answers 400). ``recruitment_id_list: ["202"]`` is the site's own
"Intern" recruitment-type facet, so internship-ness comes from structured
data rather than title parsing. Each posting carries a stable numeric string
``id`` and a ``city_info`` tree whose ``location_type == 1`` ancestor is the
country.
"""

from ... import http

SEARCH_URL = "https://api.lifeattiktok.com/api/v1/public/supplier/search/job/posts"
DETAIL_URL = "https://lifeattiktok.com/search/{job_id}"

INTERN_RECRUITMENT_ID = "202"
_PAGE_SIZE = 100


def _country(city_info: dict | None) -> str | None:
    node = city_info or {}
    while node:
        if node.get("location_type") == 1:
            return node.get("en_name")
        node = node.get("parent")
    return None


def intern_postings() -> list[dict]:
    """Every intern-typed posting, annotated with its resolved country."""
    postings = []
    offset = 0
    with http.session() as session:
        while True:
            response = session.post(
                SEARCH_URL,
                headers={"website-path": "tiktok"},
                json={
                    "keyword": "",
                    "limit": _PAGE_SIZE,
                    "offset": offset,
                    "job_category_id_list": [],
                    "location_code_list": [],
                    "subject_id_list": [],
                    "recruitment_id_list": [INTERN_RECRUITMENT_ID],
                },
            )
            response.raise_for_status()
            data = response.json().get("data") or {}
            page = data.get("job_post_list") or []
            for post in page:
                job_id = post.get("id")
                if not job_id:
                    continue
                city_info = post.get("city_info")
                city = (city_info or {}).get("en_name")
                postings.append(
                    {
                        "id": str(job_id),
                        "title": post.get("title", ""),
                        "city": city,
                        "country": _country(city_info),
                        "url": DETAIL_URL.format(job_id=job_id),
                    }
                )
            offset += len(page)
            if not page or offset >= int(data.get("count") or 0):
                break
    return postings
