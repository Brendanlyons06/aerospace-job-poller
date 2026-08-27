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
           next_digest_at = CASE WHEN frequency = 'weekly' THEN
               ((date_trunc('week', NOW() AT TIME ZONE 'America/Los_Angeles')::date
                   + 7 + TIME '09:00') AT TIME ZONE 'America/Los_Angeles')
               ELSE
               (((NOW() AT TIME ZONE 'America/Los_Angeles')::date
                   + 1 + TIME '09:00') AT TIME ZONE 'America/Los_Angeles')
               END,
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

CREATE OR REPLACE FUNCTION public.get_email_subscription(p_token TEXT)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    subscription RECORD;
BEGIN
    SELECT frequency, discipline, sector, company, state, unsubscribed_at
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
        'state', subscription.state
    );
END;
$$;

CREATE OR REPLACE FUNCTION public.update_email_subscription(
    p_token TEXT,
    p_frequency TEXT,
    p_discipline TEXT DEFAULT NULL,
    p_sector TEXT DEFAULT NULL,
    p_company TEXT DEFAULT NULL,
    p_state TEXT DEFAULT NULL
) RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF COALESCE(p_frequency, '') NOT IN ('daily', 'weekly')
       OR LENGTH(COALESCE(p_discipline, '')) > 100
       OR LENGTH(COALESCE(p_sector, '')) > 100
       OR LENGTH(COALESCE(p_company, '')) > 100
       OR LENGTH(COALESCE(p_state, '')) > 2 THEN
        RETURN 'invalid';
    END IF;

    UPDATE public.email_subscriptions
       SET frequency = p_frequency,
           discipline = NULLIF(TRIM(p_discipline), ''),
           sector = NULLIF(TRIM(p_sector), ''),
           company = NULLIF(TRIM(p_company), ''),
           state = NULLIF(UPPER(TRIM(p_state)), ''),
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

CREATE OR REPLACE FUNCTION public.delete_email_subscription(p_token TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    DELETE FROM public.email_subscriptions WHERE unsubscribe_token = p_token;
    RETURN CASE WHEN FOUND THEN 'deleted' ELSE 'invalid' END;
END;
$$;

REVOKE ALL ON FUNCTION public.confirm_email_subscription(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_email_subscription(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.update_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.delete_email_subscription(TEXT) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.confirm_email_subscription(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.confirm_email_subscription(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_email_subscription(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.get_email_subscription(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.update_email_subscription(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.delete_email_subscription(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.delete_email_subscription(TEXT) TO authenticated;
