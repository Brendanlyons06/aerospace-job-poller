CREATE OR REPLACE FUNCTION public.confirm_email_subscription_with_controls(p_token TEXT)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    confirmation_status TEXT;
    manage_token TEXT;
BEGIN
    confirmation_status := public.confirm_email_subscription(p_token);
    IF confirmation_status <> 'confirmed' THEN
        RETURN jsonb_build_object('status', confirmation_status);
    END IF;

    SELECT unsubscribe_token INTO manage_token
      FROM public.email_subscriptions
     WHERE verification_token = p_token
       AND confirmed_at IS NOT NULL
       AND unsubscribed_at IS NULL;
    IF NOT FOUND THEN
        RETURN jsonb_build_object('status', 'invalid');
    END IF;
    RETURN jsonb_build_object(
        'status', 'confirmed',
        'manage_token', manage_token
    );
END;
$$;

REVOKE ALL ON FUNCTION public.confirm_email_subscription_with_controls(TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.confirm_email_subscription_with_controls(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.confirm_email_subscription_with_controls(TEXT) TO authenticated;
