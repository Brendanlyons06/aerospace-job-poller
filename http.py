"""Shared HTTP session for every company client.

Use `http.session()` (or `http.get_json()`) instead of calling `requests`
directly. The reason is `watch.py`'s thread pool: a request with no timeout
hangs its worker *forever*, and there is no way to kill a stuck thread from
outside. One career site going dark would permanently burn a pool slot, and
enough of them would stall the whole poll. A plain `requests.Session` makes
that failure mode opt-out (you must remember `timeout=`); this one makes it
opt-in.

So the timeout here is not a tuning knob — it's what keeps a bad site from
taking down the run. Pass an explicit `timeout=` to any individual call that
genuinely needs longer.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# (connect, read). Worst case per call with RETRIES=2 is roughly
# 3 * (5 + 15) + backoff ~= 62s before the fetch gives up and the worker is
# released. Keep the product of these in mind if you raise either.
DEFAULT_TIMEOUT = (5, 15)
RETRIES = 2

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)


class _TimeoutSession(requests.Session):
    """Session that applies DEFAULT_TIMEOUT to any call that omits one."""

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return super().request(*args, **kwargs)


def session(retries: int = RETRIES) -> requests.Session:
    """A browser-shaped session with timeouts and retries already wired in.

    Retries cover POST as well as GET because job-board queries are reads
    even when they're POSTed (GraphQL search endpoints). Don't use this
    session for anything that mutates remote state.
    """
    sess = _TimeoutSession()
    sess.headers["user-agent"] = USER_AGENT
    adapter = HTTPAdapter(
        max_retries=Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
        ),
        # watch.py fetches companies concurrently but each company gets its
        # own session, so a small pool per session is plenty.
        pool_maxsize=4,
    )
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess


def get_json(url: str, **kwargs) -> dict | list:
    """One-shot GET returning parsed JSON. For boards with a plain REST API."""
    sess = session()
    try:
        resp = sess.get(url, **kwargs)
        resp.raise_for_status()
        return resp.json()
    finally:
        sess.close()
