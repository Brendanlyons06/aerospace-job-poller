"""Send a sample job-alert text + email through the real notify.py path.

Useful for confirming Twilio/SMTP credentials and formatting work end to
end, without needing an actual new posting to show up. Run with:
    python -m careers.send_test_notification
"""

from . import notify

TEST_JOB = {
    "id": "test-0001",
    "title": "Software Engineer Intern",
    "locations": ["Menlo Park, CA"],
    "url": "https://example.com/jobs/test-0001/",
}


def run() -> None:
    notify.notify_new_job("Test Company", TEST_JOB)
    print("Sent test notification.")


if __name__ == "__main__":
    run()
