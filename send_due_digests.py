"""Process due AeroScout subscriber email without polling every career site.

This entry point is intentionally small so GitHub Actions can run morning
digests independently from the best-effort hourly career-site poll schedule.
Digest completion is idempotent: after a successful delivery, the database
moves the subscription to its next daily or weekly boundary, so redundant
scheduled runs do not resend the same digest.
"""

from . import db, notify
from .watch import _process_public_subscriptions


def run() -> None:
    backend = db.validate_configuration()
    print(f"database backend: {backend}")
    notify.validate_configuration()
    _process_public_subscriptions()


if __name__ == "__main__":
    run()
