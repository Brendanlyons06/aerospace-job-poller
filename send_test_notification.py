"""Send a sample job alert through every enabled notification channel.

Useful for confirming Twilio/SMTP credentials and formatting work end to
end, without needing an actual new posting to show up. Run with:
    python -m careers.send_test_notification
"""

from . import notify

TEST_JOB = {
    "id": "test-0001",
    "title": "Mechanical Engineering Intern",
    "locations": ["Long Beach, CA"],
    "url": "https://example.com/jobs/test-0001/",
}


def run() -> None:
    delivered = notify.notify_new_job("Test Aerospace Company", TEST_JOB)
    print(f"Sent test notification through: {', '.join(delivered)}")


if __name__ == "__main__":
    run()
