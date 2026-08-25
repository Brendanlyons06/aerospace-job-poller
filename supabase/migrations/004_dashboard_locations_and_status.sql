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
                'country', jl.country
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
    (SELECT COUNT(*) FROM public.companies) AS career_source_count;

REVOKE ALL ON public.dashboard_status FROM PUBLIC;

GRANT SELECT ON public.dashboard_status TO anon;

GRANT SELECT ON public.dashboard_status TO authenticated;
