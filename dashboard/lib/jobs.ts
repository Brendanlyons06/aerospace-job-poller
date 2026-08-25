import { summarizeLocations, type LocationItem } from './locations';

export type DashboardJob = {
  company: string;
  jobId: string;
  title: string;
  url: string | null;
  sector: string | null;
  discipline: string | null;
  workMode: string | null;
  employmentType: string | null;
  postedAt: string | null;
  closesAt: string | null;
  firstSeen: string;
  location: string;
  fullLocation: string;
  locations: string[];
  locationStates: string[];
};

export type DashboardSource = {
  company: string;
  sector: string | null;
  careersUrl: string | null;
  status: 'healthy' | 'no-open-roles' | 'degraded' | 'failing' | 'pending';
  checkedAt: string | null;
  activeJobCount: number;
  consecutiveFailures: number;
};

type SupabaseJob = {
  company: string;
  job_id: string;
  title: string;
  url: string;
  sector: string | null;
  discipline: string | null;
  work_mode: string | null;
  employment_type: string | null;
  posted_at: string | null;
  closes_at: string | null;
  first_seen: string;
  location_items: LocationItem[] | null;
  location_display: string | null;
};

type SupabaseStatus = {
  refreshed_at: string | null;
  career_source_count: number | string;
  active_job_count: number | string;
  healthy_source_count: number | string;
  warning_source_count: number | string;
};

type SupabaseSource = {
  company: string;
  sector: string | null;
  careers_url: string | null;
  status: DashboardSource['status'];
  checked_at: string | null;
  active_job_count: number | string;
  consecutive_failures: number | string;
};

const demoJobs: DashboardJob[] = [
  { company: 'Anduril', jobId: 'demo-1', title: '2027 Mechanical Engineer Intern', url: null, sector: 'aerospace-defense', discipline: 'mechanical', workMode: 'on-site', employmentType: 'internship', postedAt: null, closesAt: null, firstSeen: new Date().toISOString(), location: 'Costa Mesa, CA', fullLocation: 'Costa Mesa, CA', locations: ['Costa Mesa, CA'], locationStates: ['CA'] },
  { company: 'Apple Hardware Engineering', jobId: 'demo-2', title: 'Hardware Engineering Internships', url: null, sector: 'advanced-manufacturing-hardware', discipline: 'electrical', workMode: 'on-site', employmentType: 'internship', postedAt: null, closesAt: null, firstSeen: new Date().toISOString(), location: 'Cupertino, CA', fullLocation: 'Cupertino, CA', locations: ['Cupertino, CA'], locationStates: ['CA'] },
  { company: 'GE Aerospace', jobId: 'demo-3', title: 'Systems Engineering Intern — Summer 2027', url: null, sector: 'aerospace-defense', discipline: 'systems', workMode: 'on-site', employmentType: 'internship', postedAt: null, closesAt: new Date(Date.now() + 10 * 86_400_000).toISOString(), firstSeen: new Date(Date.now() - 86_400_000).toISOString(), location: 'Evendale, OH · Arkansas City, KS · Asheville, NC · +1 more', fullLocation: 'Evendale, OH · Arkansas City, KS · Asheville, NC · Auburn, AL', locations: ['Evendale, OH', 'Arkansas City, KS', 'Asheville, NC', 'Auburn, AL'], locationStates: ['OH', 'KS', 'NC', 'AL'] },
  { company: 'Zipline', jobId: 'demo-4', title: 'Aerodynamics Intern — Summer 2027', url: null, sector: 'advanced-aircraft-autonomy', discipline: 'aerodynamics', workMode: 'on-site', employmentType: 'internship', postedAt: null, closesAt: null, firstSeen: new Date(Date.now() - 86_400_000).toISOString(), location: 'South San Francisco, CA', fullLocation: 'South San Francisco, CA', locations: ['South San Francisco, CA'], locationStates: ['CA'] },
];

const demoSources: DashboardSource[] = [
  { company: 'Anduril', sector: 'aerospace-defense', careersUrl: null, status: 'healthy', checkedAt: new Date().toISOString(), activeJobCount: 1, consecutiveFailures: 0 },
  { company: 'GE Aerospace', sector: 'aerospace-defense', careersUrl: null, status: 'healthy', checkedAt: new Date().toISOString(), activeJobCount: 1, consecutiveFailures: 0 },
];

export type JobsResult = {
  jobs: DashboardJob[];
  sources: DashboardSource[];
  source: 'live' | 'demo';
  notice: string;
  lastRefreshedAt: string | null;
  sourceCount: number;
  activeJobCount: number;
  healthySourceCount: number;
  warningSourceCount: number;
};

export async function getDashboardJobs(): Promise<JobsResult> {
  const url = process.env.SUPABASE_URL?.replace(/\/$/, '');
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) {
    return { jobs: demoJobs, sources: demoSources, source: 'demo', notice: 'Preview data — add the two Supabase dashboard settings to display your live job feed.', lastRefreshedAt: null, sourceCount: 50, activeJobCount: demoJobs.length, healthySourceCount: 50, warningSourceCount: 0 };
  }

  try {
    const headers = { apikey: key, Authorization: `Bearer ${key}` };
    const [response, statusResponse, sourcesResponse] = await Promise.all([
      fetch(`${url}/rest/v1/dashboard_active_jobs?select=*&order=first_seen.desc`, { headers, cache: 'no-store' }),
      fetch(`${url}/rest/v1/dashboard_status?select=*&limit=1`, { headers, cache: 'no-store' }),
      fetch(`${url}/rest/v1/dashboard_sources?select=*&order=company.asc`, { headers, cache: 'no-store' }),
    ]);
    if (!response.ok) throw new Error(`Supabase returned ${response.status}`);
    const rows = (await response.json()) as SupabaseJob[];
    const statusRows = statusResponse.ok ? (await statusResponse.json()) as SupabaseStatus[] : [];
    const sourceRows = sourcesResponse.ok ? (await sourcesResponse.json()) as SupabaseSource[] : [];
    const status = statusRows[0];
    return {
      source: 'live',
      notice: 'Live data from the hourly job poller.',
      lastRefreshedAt: status?.refreshed_at || null,
      sourceCount: Number(status?.career_source_count) || 50,
      activeJobCount: Number(status?.active_job_count) || rows.length,
      healthySourceCount: Number(status?.healthy_source_count) || sourceRows.filter((item) => item.status !== 'degraded' && item.status !== 'failing').length,
      warningSourceCount: Number(status?.warning_source_count) || sourceRows.filter((item) => item.status === 'degraded' || item.status === 'failing').length,
      sources: sourceRows.map((row) => ({
        company: row.company,
        sector: row.sector,
        careersUrl: row.careers_url,
        status: row.status,
        checkedAt: row.checked_at,
        activeJobCount: Number(row.active_job_count) || 0,
        consecutiveFailures: Number(row.consecutive_failures) || 0,
      })),
      jobs: rows.map((row) => {
        const locations = summarizeLocations(row.location_items, row.location_display);
        return {
          company: row.company,
          jobId: row.job_id,
          title: row.title,
          url: row.url || null,
          sector: row.sector,
          discipline: row.discipline,
          workMode: row.work_mode,
          employmentType: row.employment_type,
          postedAt: row.posted_at,
          closesAt: row.closes_at,
          firstSeen: row.first_seen,
          location: locations.display,
          fullLocation: locations.full,
          locations: locations.values,
          locationStates: locations.states,
        };
      }),
    };
  } catch {
    return { jobs: demoJobs, sources: demoSources, source: 'demo', notice: 'The live feed could not be reached, so preview data is shown.', lastRefreshedAt: null, sourceCount: 50, activeJobCount: demoJobs.length, healthySourceCount: 50, warningSourceCount: 0 };
  }
}
