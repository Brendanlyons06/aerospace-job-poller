export type DashboardJob = {
  company: string;
  jobId: string;
  title: string;
  url: string | null;
  sector: string | null;
  discipline: string | null;
  workMode: string | null;
  postedAt: string | null;
  firstSeen: string;
  location: string;
};

type SupabaseJob = {
  company: string;
  job_id: string;
  title: string;
  url: string;
  sector: string | null;
  discipline: string | null;
  work_mode: string | null;
  posted_at: string | null;
  first_seen: string;
  location_display: string | null;
};

const demoJobs: DashboardJob[] = [
  { company: 'Anduril', jobId: 'demo-1', title: '2027 Mechanical Engineer Intern', url: null, sector: 'Defense', discipline: 'Mechanical', workMode: 'On-site', postedAt: null, firstSeen: new Date().toISOString(), location: 'Costa Mesa, CA' },
  { company: 'Apple', jobId: 'demo-2', title: 'Hardware Engineering Internships', url: null, sector: 'Advanced Manufacturing', discipline: 'Mechanical', workMode: 'On-site', postedAt: null, firstSeen: new Date().toISOString(), location: 'Cupertino, CA' },
  { company: 'GE Aerospace', jobId: 'demo-3', title: 'Systems Engineering Intern — Summer 2027', url: null, sector: 'Aerospace', discipline: 'Systems', workMode: 'On-site', postedAt: null, firstSeen: new Date(Date.now() - 86_400_000).toISOString(), location: 'Evendale, OH' },
  { company: 'Zipline', jobId: 'demo-4', title: 'Aerodynamics Intern — Summer 2027', url: null, sector: 'Aircraft & eVTOL', discipline: 'Aerospace', workMode: 'On-site', postedAt: null, firstSeen: new Date(Date.now() - 86_400_000).toISOString(), location: 'South San Francisco, CA' },
];

export type JobsResult = { jobs: DashboardJob[]; source: 'live' | 'demo'; notice: string };

export async function getDashboardJobs(): Promise<JobsResult> {
  const url = process.env.SUPABASE_URL?.replace(/\/$/, '');
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) {
    return { jobs: demoJobs, source: 'demo', notice: 'Preview data — add the two Supabase dashboard settings to display your live job feed.' };
  }

  try {
    const response = await fetch(`${url}/rest/v1/dashboard_active_jobs?select=*&order=first_seen.desc`, {
      headers: { apikey: key, Authorization: `Bearer ${key}` },
      cache: 'no-store',
    });
    if (!response.ok) throw new Error(`Supabase returned ${response.status}`);
    const rows = (await response.json()) as SupabaseJob[];
    return {
      source: 'live',
      notice: 'Live data from the hourly job poller.',
      jobs: rows.map((row) => ({
        company: row.company,
        jobId: row.job_id,
        title: row.title,
        url: row.url || null,
        sector: row.sector,
        discipline: row.discipline,
        workMode: row.work_mode,
        postedAt: row.posted_at,
        firstSeen: row.first_seen,
        location: row.location_display || 'Location not listed',
      })),
    };
  } catch {
    return { jobs: demoJobs, source: 'demo', notice: 'The live feed could not be reached, so preview data is shown.' };
  }
}
