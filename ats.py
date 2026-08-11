"""Deprecated shim — the hosted-board helpers live in ``companies/feeds.py``.

New adapters should import from ``..feeds`` directly, which also carries the
richer internship-focused helpers (``greenhouse_internships_us``,
``ashby_internships_us``, ``lever_internships_us``, ``workday_internships_us``,
``phenom_internships_us``, ``eightfold_internships_us``). This module only
keeps the original ``greenhouse``/``lever`` names importable.
"""

from . import http  # noqa: F401  (kept for callers/tests that patch ats.http)
from .companies.feeds import greenhouse_jobs as greenhouse  # noqa: F401
from .companies.feeds import lever_jobs as lever  # noqa: F401
