ALTER TABLE public.email_subscriptions
    ADD COLUMN IF NOT EXISTS states TEXT,
    ADD COLUMN IF NOT EXISTS manage_requested_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS manage_sent_at TIMESTAMPTZ;

UPDATE public.email_subscriptions
   SET states = UPPER(TRIM(state))
 WHERE states IS NULL AND state IS NOT NULL;

CREATE INDEX IF NOT EXISTS email_subscriptions_manage_pending_idx
    ON public.email_subscriptions (manage_requested_at)
    WHERE confirmed_at IS NOT NULL
      AND unsubscribed_at IS NULL
      AND manage_sent_at IS NULL;

CREATE OR REPLACE FUNCTION public.request_email_subscription(
    p_email TEXT,
    p_frequency TEXT DEFAULT 'daily',
    p_discipline TEXT DEFAULT NULL,
    p_sector TEXT DEFAULT NULL,
    p_company TEXT DEFAULT NULL,
    p_states TEXT[] DEFAULT NULL,
    p_website TEXT DEFAULT NULL
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    normalized_email TEXT := LOWER(TRIM(COALESCE(p_email, '')));
    normalized_states TEXT[] := ARRAY(
        SELECT DISTINCT UPPER(TRIM(value))
          FROM unnest(COALESCE(p_states, ARRAY[]::TEXT[])) AS value
         WHERE TRIM(value) <> ''
    );
    existing_confirmed TIMESTAMPTZ;
BEGIN
    IF COALESCE(TRIM(p_website), '') <> '' THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;
    IF LENGTH(normalized_email) > 254
       OR normalized_email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$'
       OR COALESCE(p_frequency, '') NOT IN ('daily', 'weekly')
       OR COALESCE(array_length(normalized_states, 1), 0) > 64
       OR EXISTS (
           SELECT 1 FROM unnest(normalized_states) AS value
            WHERE value <> 'REMOTE' AND value !~ '^[A-Z]{2}$'
       ) THEN
        RETURN jsonb_build_object('accepted', FALSE);
    END IF;

    SELECT confirmed_at INTO existing_confirmed
      FROM public.email_subscriptions
     WHERE email = normalized_email AND unsubscribed_at IS NULL;
    IF existing_confirmed IS NOT NULL THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;

    IF (SELECT COUNT(*) FROM public.email_subscriptions
         WHERE verification_requested_at > NOW() - INTERVAL '1 hour') >= 20
       OR (SELECT COUNT(*) FROM public.email_subscriptions
            WHERE confirmed_at IS NULL AND created_at > NOW() - INTERVAL '30 days') >= 250
       OR EXISTS (
           SELECT 1 FROM public.email_subscriptions
            WHERE email = normalized_email
              AND verification_requested_at > NOW() - INTERVAL '24 hours'
              AND unsubscribed_at IS NULL
       ) THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;

    INSERT INTO public.email_subscriptions (
        email, frequency, discipline, sector, company, state, states,
        verification_token, unsubscribe_token, created_at,
        verification_requested_at, verification_sent_at, confirmed_at,
        unsubscribed_at, last_digest_at, next_digest_at,
        consecutive_failures, last_error
    ) VALUES (
        normalized_email, p_frequency, NULLIF(TRIM(p_discipline), ''),
        NULLIF(TRIM(p_sector), ''), NULLIF(TRIM(p_company), ''),
        normalized_states[1], NULLIF(array_to_string(normalized_states, ','), ''),
        gen_random_uuid()::TEXT, gen_random_uuid()::TEXT, NOW(), NOW(), NULL,
        NULL, NULL, NULL, NULL, 0, NULL
    )
    ON CONFLICT (email) DO UPDATE SET
        frequency = EXCLUDED.frequency,
        discipline = EXCLUDED.discipline,
        sector = EXCLUDED.sector,
        company = EXCLUDED.company,
        state = EXCLUDED.state,
        states = EXCLUDED.states,
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

CREATE OR REPLACE FUNCTION public.request_subscription_management(
    p_email TEXT,
    p_website TEXT DEFAULT NULL
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    normalized_email TEXT := LOWER(TRIM(COALESCE(p_email, '')));
BEGIN
    IF COALESCE(TRIM(p_website), '') <> ''
       OR LENGTH(normalized_email) > 254
       OR normalized_email !~* '^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$' THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;
    IF (SELECT COUNT(*) FROM public.email_subscriptions
         WHERE manage_requested_at > NOW() - INTERVAL '1 hour') >= 20 THEN
        RETURN jsonb_build_object('accepted', TRUE);
    END IF;

    UPDATE public.email_subscriptions
       SET manage_requested_at = NOW(), manage_sent_at = NULL
     WHERE email = normalized_email
       AND confirmed_at IS NOT NULL
       AND unsubscribed_at IS NULL
       AND (manage_requested_at IS NULL
            OR manage_requested_at <= NOW() - INTERVAL '1 hour');

    RETURN jsonb_build_object('accepted', TRUE);
END;
$$;

CREATE OR REPLACE FUNCTION public.get_email_subscription(p_token TEXT)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    subscription RECORD;
BEGIN
    SELECT frequency, discipline, sector, company, state, states, unsubscribed_at
      INTO subscription
      FROM public.email_subscriptions
     WHERE unsubscribe_token = p_token
       AND confirmed_at IS NOT NULL;
    IF NOT FOUND THEN
        RETURN jsonb_build_object('status', 'invalid');
    END IF;
    RETURN jsonb_build_object(
        'status', CASE WHEN subscription.unsubscribed_at IS NULL
                       THEN 'active' ELSE 'unsubscribed' END,
        'frequency', subscription.frequency,
        'discipline', subscription.discipline,
        'sector', subscription.sector,
        'company', subscription.company,
        'state', subscription.state,
        'states', COALESCE(
            to_jsonb(string_to_array(NULLIF(subscription.states, ''), ',')),
            CASE WHEN subscription.state IS NULL THEN '[]'::jsonb
                 ELSE jsonb_build_array(subscription.state) END
        )
    );
END;
$$;

CREATE OR REPLACE FUNCTION public.update_email_subscription(
    p_token TEXT,
    p_frequency TEXT,
    p_discipline TEXT DEFAULT NULL,
    p_sector TEXT DEFAULT NULL,
    p_company TEXT DEFAULT NULL,
    p_states TEXT[] DEFAULT NULL
) RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    normalized_states TEXT[] := ARRAY(
        SELECT DISTINCT UPPER(TRIM(value))
          FROM unnest(COALESCE(p_states, ARRAY[]::TEXT[])) AS value
         WHERE TRIM(value) <> ''
    );
BEGIN
    IF COALESCE(p_frequency, '') NOT IN ('daily', 'weekly')
       OR LENGTH(COALESCE(p_discipline, '')) > 100
       OR LENGTH(COALESCE(p_sector, '')) > 100
       OR LENGTH(COALESCE(p_company, '')) > 100
       OR COALESCE(array_length(normalized_states, 1), 0) > 64
       OR EXISTS (
           SELECT 1 FROM unnest(normalized_states) AS value
            WHERE value <> 'REMOTE' AND value !~ '^[A-Z]{2}$'
       ) THEN
        RETURN 'invalid';
    END IF;

    UPDATE public.email_subscriptions
       SET frequency = p_frequency,
           discipline = NULLIF(TRIM(p_discipline), ''),
           sector = NULLIF(TRIM(p_sector), ''),
           company = NULLIF(TRIM(p_company), ''),
           state = normalized_states[1],
           states = NULLIF(array_to_string(normalized_states, ','), ''),
           next_digest_at = CASE WHEN p_frequency = 'weekly' THEN
               ((date_trunc('week', NOW() AT TIME ZONE 'America/Los_Angeles')::date
                   + 7 + TIME '09:00') AT TIME ZONE 'America/Los_Angeles')
               ELSE
               (((NOW() AT TIME ZONE 'America/Los_Angeles')::date
                   + 1 + TIME '09:00') AT TIME ZONE 'America/Los_Angeles')
               END
     WHERE unsubscribe_token = p_token
       AND confirmed_at IS NOT NULL
       AND unsubscribed_at IS NULL;
    RETURN CASE WHEN FOUND THEN 'updated' ELSE 'invalid' END;
END;
$$;

REVOKE ALL ON FUNCTION public.request_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT[], TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.request_subscription_management(TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_email_subscription(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.update_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT[]) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.request_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT[], TEXT) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.request_subscription_management(TEXT, TEXT) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_email_subscription(TEXT) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.update_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT[]) TO anon, authenticated;
