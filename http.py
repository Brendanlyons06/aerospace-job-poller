"""Shared curl_cffi session for every company client.

Use `http.session()` (or `http.get_json()`) instead of calling an HTTP client
directly. The reason is `watch.py`'s thread pool: a request with no timeout
hangs its worker *forever*, and there is no way to kill a stuck thread from
outside. One career site going dark would permanently burn a pool slot, and
enough of them would stall the whole poll. This wrapper makes timeouts
opt-out, and uses curl_cffi's browser-like TLS fingerprint for sites that
block Python's default HTTP stack.

So the timeout here is not a tuning knob — it's what keeps a bad site from
taking down the run. Pass an explicit `timeout=` to any individual call that
genuinely needs longer.
"""

import time
from urllib.parse import urlsplit

from curl_cffi import requests

from . import observability

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
    """curl_cffi session that applies timeouts and retries read requests."""

    def __init__(self, retries: int) -> None:
        # `impersonate` aligns the TLS and HTTP fingerprint with Chrome. The
        # explicit user agent below remains useful to clients that log it.
        super().__init__(impersonate="chrome")
        self._retries = retries
        self.headers["user-agent"] = USER_AGENT

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        method = str(args[0] if args else kwargs.get("method", "GET")).upper()
        url = str(args[1] if len(args) > 1 else kwargs.get("url", ""))
        parsed = urlsplit(url)
        endpoint = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        for attempt in range(self._retries + 1):
            started = time.monotonic()
            try:
                response = super().request(*args, **kwargs)
                retryable = response.status_code in {429, 500, 502, 503, 504}
                observability.log_event(
                    event="http_request",
                    method=method,
                    endpoint=endpoint,
                    attempt=attempt + 1,
                    duration_ms=round((time.monotonic() - started) * 1000),
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type"),
                    content_length=response.headers.get("content-length"),
                    will_retry=retryable and attempt < self._retries,
                )
                if not retryable:
                    return response
            except requests.exceptions.RequestException as exc:
                observability.log_event(
                    event="http_request_error",
                    method=method,
                    endpoint=endpoint,
                    attempt=attempt + 1,
                    duration_ms=round((time.monotonic() - started) * 1000),
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    will_retry=attempt < self._retries,
                )
                if attempt == self._retries:
                    raise

            if attempt < self._retries:
                time.sleep(0.5 * (2**attempt))

        # The final response is deliberately returned so callers retain the
        # usual `raise_for_status()` behavior and error details.
        return response


def session(retries: int = RETRIES) -> requests.Session:
    """A browser-shaped session with timeouts and retries already wired in.

    Retries cover POST as well as GET because job-board queries are reads
    even when they're POSTed (GraphQL search endpoints). Don't use this
    session for anything that mutates remote state.
    """
    return _TimeoutSession(max(retries, 0))


def get_json(url: str, **kwargs) -> dict | list:
    """One-shot GET returning parsed JSON. For boards with a plain REST API."""
    sess = session()
    try:
        resp = sess.get(url, **kwargs)
        resp.raise_for_status()
        return resp.json()
    finally:
        sess.close()
