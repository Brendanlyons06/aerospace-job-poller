import { pollFreshness, type DashboardSource } from './jobs';

type OwnerStatusRow = {
  last_poll_completed_at: string | null;
  last_digest_completed_at: string | null;
  career_source_count: number | string;
  active_job_count: number | string;
  warning_source_count: number | string;
  active_subscriber_count: number | string;
  pending_subscriber_count: number | string;
  unsubscribed_count: number | string;
  delivery_failure_count: number | string;
  latest_subscriber_digest_at: string | null;
  next_subscriber_digest_at: string | null;
  emails_sent_today: number | string;
  subscriber_cap: number | string;
  daily_email_cap: number | string;
};

type SourceRow = {
  company: string;
  sector: string | null;
  careers_url: string | null;
  status: DashboardSource['status'];
  checked_at: string | null;
  active_job_count: number | string;
  consecutive_failures: number | string;
};

export type OwnerStatus = {
  lastPollAt: string | null;
  lastDigestAt: string | null;
  latestSubscriberDigestAt: string | null;
  nextSubscriberDigestAt: string | null;
  sourceCount: number;
  activeJobCount: number;
  warningSourceCount: number;
  activeSubscribers: number;
  pendingSubscribers: number;
  unsubscribed: number;
  deliveryFailures: number;
  emailsSentToday: number;
  subscriberCap: number;
  dailyEmailCap: number;
  pollStatus: 'healthy' | 'delayed' | 'stale' | 'unknown';
  pollAgeMinutes: number | null;
  warningSources: DashboardSource[];
};

export async function getOwnerStatus(): Promise<OwnerStatus | null> {
  const url = process.env.SUPABASE_URL?.replace(/\/$/, '');
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  const requestHeaders = { apikey: key, Authorization: `Bearer ${key}` };
  try {
    const [statusResponse, sourcesResponse] = await Promise.all([
      fetch(`${url}/rest/v1/dashboard_owner_status?select=*&limit=1`, { headers: requestHeaders, cache: 'no-store' }),
      fetch(`${url}/rest/v1/dashboard_sources?select=*&status=in.(degraded,failing)&order=company.asc`, { headers: requestHeaders, cache: 'no-store' }),
    ]);
    if (!statusResponse.ok || !sourcesResponse.ok) return null;
    const row = ((await statusResponse.json()) as OwnerStatusRow[])[0];
    if (!row) return null;
    const sources = (await sourcesResponse.json()) as SourceRow[];
    const freshness = pollFreshness(row.last_poll_completed_at);
    return {
      lastPollAt: row.last_poll_completed_at,
      lastDigestAt: row.last_digest_completed_at,
      latestSubscriberDigestAt: row.latest_subscriber_digest_at,
      nextSubscriberDigestAt: row.next_subscriber_digest_at,
      sourceCount: Number(row.career_source_count) || 0,
      activeJobCount: Number(row.active_job_count) || 0,
      warningSourceCount: Number(row.warning_source_count) || 0,
      activeSubscribers: Number(row.active_subscriber_count) || 0,
      pendingSubscribers: Number(row.pending_subscriber_count) || 0,
      unsubscribed: Number(row.unsubscribed_count) || 0,
      deliveryFailures: Number(row.delivery_failure_count) || 0,
      emailsSentToday: Number(row.emails_sent_today) || 0,
      subscriberCap: Number(row.subscriber_cap) || 100,
      dailyEmailCap: Number(row.daily_email_cap) || 200,
      pollStatus: freshness.status,
      pollAgeMinutes: freshness.ageMinutes,
      warningSources: sources.map((source) => ({
        company: source.company,
        sector: source.sector,
        careersUrl: source.careers_url,
        status: source.status,
        checkedAt: source.checked_at,
        activeJobCount: Number(source.active_job_count) || 0,
        consecutiveFailures: Number(source.consecutive_failures) || 0,
      })),
    };
  } catch {
    return null;
  }
}
