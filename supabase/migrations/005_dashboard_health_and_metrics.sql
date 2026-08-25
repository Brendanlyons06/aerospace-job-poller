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
      WHERE COALESCE(h.consecutive_failures, 0) > 0) AS warning_source_count;

REVOKE ALL ON public.dashboard_status FROM PUBLIC;

GRANT SELECT ON public.dashboard_status TO anon;

GRANT SELECT ON public.dashboard_status TO authenticated;

DROP VIEW IF EXISTS public.dashboard_sources;

CREATE VIEW public.dashboard_sources AS
SELECT
    c.company,
    c.sector,
    c.careers_url,
    CASE
        WHEN COALESCE(h.consecutive_failures, 0) >= 3 THEN 'failing'
        WHEN COALESCE(h.consecutive_failures, 0) > 0 THEN 'degraded'
        WHEN COALESCE(h.consecutive_zero, 0) >= 3 THEN 'no-open-roles'
        WHEN h.last_success IS NULL AND h.last_failure IS NULL THEN 'pending'
        ELSE 'healthy'
    END AS status,
    GREATEST(h.last_success, h.last_failure) AS checked_at,
    COALESCE(h.last_job_count, 0) AS active_job_count,
    COALESCE(h.consecutive_failures, 0) AS consecutive_failures
FROM public.companies AS c
LEFT JOIN public.company_health AS h ON h.company = c.company;

REVOKE ALL ON public.dashboard_sources FROM PUBLIC;

GRANT SELECT ON public.dashboard_sources TO anon;

GRANT SELECT ON public.dashboard_sources TO authenticated;
