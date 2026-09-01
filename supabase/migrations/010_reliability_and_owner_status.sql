DROP VIEW IF EXISTS public.dashboard_owner_status;

CREATE VIEW public.dashboard_owner_status AS
SELECT
    (SELECT value FROM public.system_meta
      WHERE key = 'last_poll_completed_at') AS last_poll_completed_at,
    (SELECT value FROM public.system_meta
      WHERE key = 'last_digest_completed_at') AS last_digest_completed_at,
    (SELECT COUNT(*) FROM public.companies) AS career_source_count,
    (SELECT COUNT(*) FROM public.jobs WHERE closed_at IS NULL) AS active_job_count,
    (SELECT COUNT(*) FROM public.companies AS c
       LEFT JOIN public.company_health AS h ON h.company = c.company
      WHERE COALESCE(h.consecutive_failures, 0) > 0) AS warning_source_count,
    (SELECT COUNT(*) FROM public.email_subscriptions
      WHERE confirmed_at IS NOT NULL AND unsubscribed_at IS NULL) AS active_subscriber_count,
    (SELECT COUNT(*) FROM public.email_subscriptions
      WHERE confirmed_at IS NULL AND unsubscribed_at IS NULL) AS pending_subscriber_count,
    (SELECT COUNT(*) FROM public.email_subscriptions
      WHERE unsubscribed_at IS NOT NULL) AS unsubscribed_count,
    (SELECT COUNT(*) FROM public.email_subscriptions
      WHERE consecutive_failures > 0) AS delivery_failure_count,
    (SELECT MAX(last_digest_at) FROM public.email_subscriptions) AS latest_subscriber_digest_at,
    (SELECT MIN(next_digest_at) FROM public.email_subscriptions
      WHERE confirmed_at IS NOT NULL AND unsubscribed_at IS NULL) AS next_subscriber_digest_at,
    COALESCE(
        (SELECT value::INTEGER FROM public.system_meta
          WHERE key = 'public_email_sent_' || CURRENT_DATE::TEXT),
        0
    ) AS emails_sent_today,
    100 AS subscriber_cap,
    200 AS daily_email_cap;

REVOKE ALL ON public.dashboard_owner_status FROM PUBLIC;

GRANT SELECT ON public.dashboard_owner_status TO anon;

GRANT SELECT ON public.dashboard_owner_status TO authenticated;
