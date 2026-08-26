CREATE TABLE IF NOT EXISTS public.email_subscriptions (
    email TEXT PRIMARY KEY,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly')),
    discipline TEXT,
    sector TEXT,
    company TEXT,
    state TEXT,
    verification_token TEXT NOT NULL,
    unsubscribe_token TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verification_requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verification_sent_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    unsubscribed_at TIMESTAMPTZ,
    last_digest_at TIMESTAMPTZ,
    next_digest_at TIMESTAMPTZ,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    last_error TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS email_subscriptions_verification_token_idx
    ON public.email_subscriptions (verification_token);

CREATE UNIQUE INDEX IF NOT EXISTS email_subscriptions_unsubscribe_token_idx
    ON public.email_subscriptions (unsubscribe_token);

CREATE INDEX IF NOT EXISTS email_subscriptions_digest_due_idx
    ON public.email_subscriptions (next_digest_at)
    WHERE confirmed_at IS NOT NULL AND unsubscribed_at IS NULL;

ALTER TABLE public.email_subscriptions ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.email_subscriptions FROM PUBLIC;
REVOKE ALL ON public.email_subscriptions FROM anon;
REVOKE ALL ON public.email_subscriptions FROM authenticated;

CREATE OR REPLACE FUNCTION public.request_email_subscription(
    p_email TEXT,
    p_frequency TEXT DEFAULT 'daily',
    p_discipline TEXT DEFAULT NULL,
    p_sector TEXT DEFAULT NULL,
    p_company TEXT DEFAULT NULL,
    p_state TEXT DEFAULT NULL,
    p_website TEXT DEFAULT NULL
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    normalized_email TEXT := LOWER(TRIM(COALESCE(p_email, '')));
    existing_confirmed TIMESTAMPTZ;
BEGIN
    IF COALESCE(TRIM(p_website), '') <> '' THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;
    IF LENGTH(normalized_email) > 254
       OR normalized_email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$' THEN
        RETURN jsonb_build_object('accepted', FALSE);
    END IF;
    IF COALESCE(p_frequency, '') NOT IN ('daily', 'weekly') THEN
        RETURN jsonb_build_object('accepted', FALSE);
    END IF;

    SELECT confirmed_at INTO existing_confirmed
      FROM public.email_subscriptions
     WHERE email = normalized_email AND unsubscribed_at IS NULL;

    IF existing_confirmed IS NOT NULL THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;

    IF (SELECT COUNT(*) FROM public.email_subscriptions
         WHERE verification_requested_at > NOW() - INTERVAL '1 hour') >= 20 THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;
    IF (SELECT COUNT(*) FROM public.email_subscriptions
         WHERE confirmed_at IS NULL AND created_at > NOW() - INTERVAL '30 days') >= 250 THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;
    IF EXISTS (
        SELECT 1 FROM public.email_subscriptions
         WHERE email = normalized_email
           AND verification_requested_at > NOW() - INTERVAL '24 hours'
           AND unsubscribed_at IS NULL
    ) THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;

    INSERT INTO public.email_subscriptions (
        email, frequency, discipline, sector, company, state,
        verification_token, unsubscribe_token, created_at,
        verification_requested_at, verification_sent_at, confirmed_at,
        unsubscribed_at, last_digest_at, next_digest_at,
        consecutive_failures, last_error
    ) VALUES (
        normalized_email, p_frequency, NULLIF(TRIM(p_discipline), ''),
        NULLIF(TRIM(p_sector), ''), NULLIF(TRIM(p_company), ''),
        NULLIF(UPPER(TRIM(p_state)), ''), gen_random_uuid()::TEXT,
        gen_random_uuid()::TEXT, NOW(), NOW(), NULL, NULL, NULL, NULL, NULL, 0, NULL
    )
    ON CONFLICT (email) DO UPDATE SET
        frequency = EXCLUDED.frequency,
        discipline = EXCLUDED.discipline,
        sector = EXCLUDED.sector,
        company = EXCLUDED.company,
        state = EXCLUDED.state,
        verification_token = gen_random_uuid()::TEXT,
        unsubscribe_token = gen_random_uuid()::TEXT,
        verification_requested_at = NOW(),
        verification_sent_at = NULL,
        confirmed_at = NULL,
        unsubscribed_at = NULL,
        last_digest_at = NULL,
        next_digest_at = NULL,
        consecutive_failures = 0,
        last_error = NULL;

    RETURN jsonb_build_object('accepted', TRUE);
END;
$$;

CREATE OR REPLACE FUNCTION public.confirm_email_subscription(p_token TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM public.email_subscriptions
                WHERE verification_token = p_token AND confirmed_at IS NOT NULL
                  AND unsubscribed_at IS NULL) THEN
        RETURN 'confirmed';
    END IF;
    IF (SELECT COUNT(*) FROM public.email_subscriptions
         WHERE confirmed_at IS NOT NULL AND unsubscribed_at IS NULL) >= 100 THEN
        RETURN 'full';
    END IF;

    UPDATE public.email_subscriptions
       SET confirmed_at = NOW(),
           unsubscribed_at = NULL,
           next_digest_at = NOW() + CASE WHEN frequency = 'weekly'
                                         THEN INTERVAL '7 days'
                                         ELSE INTERVAL '1 day' END,
           consecutive_failures = 0,
           last_error = NULL
     WHERE verification_token = p_token
       AND confirmed_at IS NULL
       AND verification_requested_at > NOW() - INTERVAL '7 days';

    IF FOUND THEN
        RETURN 'confirmed';
    END IF;
    RETURN 'invalid';
END;
$$;

CREATE OR REPLACE FUNCTION public.unsubscribe_email_subscription(p_token TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    UPDATE public.email_subscriptions
       SET unsubscribed_at = NOW(), next_digest_at = NULL
     WHERE unsubscribe_token = p_token AND unsubscribed_at IS NULL;
    RETURN CASE WHEN FOUND THEN 'unsubscribed' ELSE 'invalid' END;
END;
$$;

REVOKE ALL ON FUNCTION public.request_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.confirm_email_subscription(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.unsubscribe_email_subscription(TEXT) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.request_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT, TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.request_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.confirm_email_subscription(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.confirm_email_subscription(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.unsubscribe_email_subscription(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.unsubscribe_email_subscription(TEXT) TO authenticated;

DROP VIEW IF EXISTS public.dashboard_active_jobs;

CREATE VIEW public.dashboard_active_jobs AS
SELECT
    j.company,
    j.job_id,
    j.title,
    j.url,
    j.sector,
    j.discipline,
    j.employment_type,
    j.work_mode,
    j.posted_at,
    j.closes_at,
    j.first_seen,
    j.last_seen,
    j.compensation_min,
    j.compensation_max,
    j.compensation_currency,
    j.compensation_period,
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'label', jl.label,
                'city', jl.city,
                'state', jl.state,
                'country', jl.country,
                'latitude', jl.latitude,
                'longitude', jl.longitude
            ) ORDER BY jl.location_index
        ) FROM public.job_locations AS jl
        WHERE jl.company = j.company AND jl.job_id = j.job_id),
        '[]'::jsonb
    ) AS location_items,
    COALESCE(
        NULLIF((SELECT string_agg(jl.label, ', ' ORDER BY jl.location_index)
                FROM public.job_locations AS jl
                WHERE jl.company = j.company AND jl.job_id = j.job_id), ''),
        j.locations
    ) AS location_display
FROM public.jobs AS j
WHERE j.closed_at IS NULL;

REVOKE ALL ON public.dashboard_active_jobs FROM PUBLIC;
GRANT SELECT ON public.dashboard_active_jobs TO anon;
GRANT SELECT ON public.dashboard_active_jobs TO authenticated;

DROP VIEW IF EXISTS public.dashboard_status;

CREATE VIEW public.dashboard_status AS
SELECT
    COALESCE(
        (SELECT value FROM public.system_meta WHERE key = 'last_poll_completed_at'),
        (SELECT MAX(last_seen) FROM public.companies)
    ) AS refreshed_at,
    (SELECT COUNT(*) FROM public.companies) AS career_source_count,
    (SELECT COUNT(*) FROM public.jobs WHERE closed_at IS NULL) AS active_job_count,
    (SELECT COUNT(*)
       FROM public.companies AS c
       LEFT JOIN public.company_health AS h ON h.company = c.company
      WHERE COALESCE(h.consecutive_failures, 0) = 0) AS healthy_source_count,
    (SELECT COUNT(*)
       FROM public.companies AS c
       LEFT JOIN public.company_health AS h ON h.company = c.company
      WHERE COALESCE(h.consecutive_failures, 0) > 0) AS warning_source_count,
    (SELECT COUNT(*) FROM public.email_subscriptions
      WHERE confirmed_at IS NOT NULL AND unsubscribed_at IS NULL) AS subscriber_count,
    100 AS subscriber_cap;

REVOKE ALL ON public.dashboard_status FROM PUBLIC;
GRANT SELECT ON public.dashboard_status TO anon;
GRANT SELECT ON public.dashboard_status TO authenticated;
