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
