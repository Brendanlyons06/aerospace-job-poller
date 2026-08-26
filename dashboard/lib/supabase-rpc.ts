export async function callSupabaseRpc(name: string, payload: Record<string, unknown>) {
  const url = process.env.SUPABASE_URL?.replace(/\/$/, '');
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) throw new Error('Subscription service is not configured');
  const response = await fetch(`${url}/rest/v1/rpc/${name}`, {
    method: 'POST',
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
    cache: 'no-store',
  });
  if (!response.ok) throw new Error(`Subscription service returned ${response.status}`);
  return response.json() as Promise<unknown>;
}
