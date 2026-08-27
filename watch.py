"""Poll every registered company for new job postings and alert on new ones.

Run repeatedly (cron / launchd / a `while true; sleep` loop) — each run
fetches, filters (each company decides its own — see companies/README.md),
diffs against careers/jobs.db, and sends a text + email for anything
genuinely new. Add a company by dropping a new folder under companies/; it's
auto-discovered.

Fetching is concurrent, everything after it is not — see MAX_WORKERS.
"""

import fcntl
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import db, notify, observability
from .companies import COMPANIES

# Fetching is I/O-bound, so this is sized by memory, not by CPU. Each
# in-flight company holds a raw response plus its parsed form; only the
# four-string job dicts outlive the fetch. Measured over 100 companies
# against 2MB responses: 1 worker = 18.8s / 28MB peak heap, 12 workers =
# 1.8s / 33MB, 100 workers = 1.5s / 148MB. Past ~12 the wall clock stops
# improving (the pool is already deeper than the latency requires) while
# peak memory keeps climbing with response size — and a board fatter than
# 2MB scales that 148MB figure linearly, into OOM range on a 1GB box.
# Raise this only if you hit a real wall-clock wall, never for tidiness.
MAX_WORKERS = 12
LOCK_PATH = db.DB_PATH.with_name(".job-poller.lock")


def _send_health_message(subject: str, body: str) -> bool:
    """Send health mail without allowing it to stop normal job polling."""
    try:
        notify.notify_system_message(subject, body)
        return True
    except Exception as exc:
        print(f"HEALTH ALERT FAILED: {type(exc).__name__}: {exc}")
        return False


def _weekly_health_body() -> str:
    rows = db.health_snapshot()
    lines = ["Weekly AeroScout poller status", ""]
    for row in rows:
        if row["consecutive_failures"]:
            status = f"FAILING ({row['consecutive_failures']} consecutive polls)"
        else:
            status = f"healthy, {row['last_job_count'] or 0} matching jobs"
        if row["consecutive_zero"]:
            status += f", zero-match streak {row['consecutive_zero']}"
        lines.append(f"{row['company']}: {status}")
    subscriptions = db.subscription_summary()
    lines.extend(
        [
            "",
            "Subscriber beta",
            f"Active: {subscriptions['active']} / {subscriptions['subscriber_cap']}",
            f"Pending verification: {subscriptions['pending']}",
            f"Unsubscribed records: {subscriptions['unsubscribed']}",
            f"Addresses with delivery failures: {subscriptions['delivery_failures']}",
            "Public emails sent today: "
            f"{subscriptions['emails_sent_today']} / {subscriptions['daily_email_cap']}",
        ]
    )
    return "\n".join(lines)


def _process_public_subscriptions() -> None:
    """Send bounded confirmation and digest batches using the existing SMTP account."""
    if not notify.PUBLIC_SUBSCRIPTIONS_ENABLED:
        return
    removed = db.cleanup_expired_subscription_requests()
    if removed:
        print(f"removed {removed} expired unconfirmed subscription request(s)")
    for subscription in db.pending_subscription_verifications(limit=10):
        if not db.public_email_send_available():
            print("PUBLIC EMAIL DAILY CAP REACHED; remaining deliveries deferred")
            break
        try:
            notify.send_subscription_verification(
                subscription["email"], subscription["verification_token"],
                subscription["unsubscribe_token"]
            )
        except Exception as exc:
            db.mark_subscription_delivery_failed(
                subscription["email"], f"{type(exc).__name__}: {exc}"
            )
            print(f"SUBSCRIPTION VERIFICATION FAILED: {type(exc).__name__}: {exc}")
        else:
            db.record_public_email_sent()
            db.mark_subscription_verification_sent(subscription["email"])

    for digest in db.due_subscription_digests(limit=20):
        try:
            if digest["jobs"]:
                if not db.public_email_send_available():
                    print("PUBLIC EMAIL DAILY CAP REACHED; remaining deliveries deferred")
                    break
                notify.send_subscription_digest(
                    digest["email"], digest["jobs"], digest["unsubscribe_token"]
                )
        except Exception as exc:
            db.mark_subscription_delivery_failed(
                digest["email"], f"{type(exc).__name__}: {exc}"
            )
            print(f"SUBSCRIPTION DIGEST FAILED: {type(exc).__name__}: {exc}")
        else:
            if digest["jobs"]:
                db.record_public_email_sent()
            db.mark_subscription_digest_complete(digest["email"], digest["frequency"])


def _fetch(company, run_id: str | None = None) -> list[dict]:
    """Fetch + filter one company. Runs on a pool thread; touches no shared state."""
    run_id = run_id or uuid.uuid4().hex
    context = observability.set_context(company.COMPANY_NAME, run_id)
    started = time.monotonic()
    try:
        jobs = company.fetch_jobs()
        raw_job_count = len(jobs)
        if hasattr(company, "filter_jobs"):
            jobs = company.filter_jobs(jobs)
        observability.log_event(
            event="fetch_complete",
            duration_ms=round((time.monotonic() - started) * 1000),
            raw_job_count=raw_job_count,
            filtered_job_count=len(jobs),
        )
        return jobs
    except Exception as exc:
        observability.log_event(
            event="fetch_failed",
            duration_ms=round((time.monotonic() - started) * 1000),
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise
    finally:
        observability.reset_context(context)


def _run_once() -> None:
    backend = db.validate_configuration()
    print(f"database backend: {backend}")
    notify.validate_configuration()
    notify.ensure_opted_in()
    started = time.monotonic()
    run_id = uuid.uuid4().hex

    # Fetch concurrently...
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_fetch, company, run_id): company for company in COMPANIES}
        results = {}
        failures = []
        for future, company in futures.items():
            try:
                results[company] = future.result()
            except Exception as exc:
                # One rotted persisted-query id or dead career site must not
                # take down the other 99 companies' polls.
                failures.append(company.COMPANY_NAME)
                error = f"{type(exc).__name__}: {exc}"
                failure_count, should_alert = db.record_poll_failure(
                    company.COMPANY_NAME, error
                )
                print(f"[{company.COMPANY_NAME}] FETCH FAILED: {type(exc).__name__}: {exc}")
                if should_alert:
                    _send_health_message(
                        f"Job poller warning: {company.COMPANY_NAME} is failing",
                        f"{company.COMPANY_NAME} has failed {failure_count} consecutive "
                        f"polls.\n\nLatest error:\n{error}",
                    )

    # ...but diff and alert serially on the main thread. sqlite doesn't want
    # concurrent writers to one file, Twilio rate-limits, and both legs are
    # fast enough that there's nothing to win by parallelizing them.
    for company, jobs in results.items():
        recovered, _zero_count = db.record_poll_success(
            company.COMPANY_NAME, len(jobs)
        )
        if recovered:
            _send_health_message(
                f"Job poller recovered: {company.COMPANY_NAME}",
                f"{company.COMPANY_NAME} is responding again and returned "
                f"{len(jobs)} matching jobs.",
            )
        sync_metadata = {}
        module_name = getattr(company, "__name__", "")
        if module_name:
            sync_metadata["company_slug"] = module_name.rsplit(".", 1)[-1]
        if getattr(company, "CAREERS_URL", None):
            sync_metadata["careers_url"] = company.CAREERS_URL
        new_jobs = db.sync_and_get_new(company.COMPANY_NAME, jobs, **sync_metadata)
        observability.log_event(
            company.COMPANY_NAME,
            "poll_result",
            run_id=run_id,
            job_count=len(jobs),
            new_job_count=len(new_jobs),
        )

        for job in new_jobs:
            print(f"[{company.COMPANY_NAME}] new: {job['title']} ({', '.join(job['locations'])})")
            try:
                notify.notify_new_job(company.COMPANY_NAME, job)
            except Exception as exc:
                db.mark_notification_failed(
                    company.COMPANY_NAME,
                    job["id"],
                    f"{type(exc).__name__}: {exc}",
                )
                print(
                    f"[{company.COMPANY_NAME}] ALERT FAILED; will retry: "
                    f"{type(exc).__name__}: {exc}"
                )
            else:
                db.mark_notification_delivered(company.COMPANY_NAME, job["id"])

        if not new_jobs:
            print(f"[{company.COMPANY_NAME}] no new postings ({len(jobs)} match filters)")

    if db.weekly_summary_due():
        if _send_health_message(
            "Weekly AeroScout poller and subscriber status", _weekly_health_body()
        ):
            db.mark_weekly_summary_sent()

    _process_public_subscriptions()

    db.mark_poll_completed()

    elapsed = time.monotonic() - started
    summary = f"polled {len(results)}/{len(COMPANIES)} companies in {elapsed:.1f}s"
    if failures:
        summary += f" — failed: {', '.join(failures)}"
    print(summary)


def run() -> None:
    """Run one poll, or skip cleanly when another poll is already active."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another poll is already running; skipped this interval")
            return
        try:
            _run_once()
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


if __name__ == "__main__":
    run()
