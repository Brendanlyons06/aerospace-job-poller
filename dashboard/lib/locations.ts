export type LocationItem = {
  label: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  latitude: number | string | null;
  longitude: number | string | null;
};

const stateCodes: Record<string, string> = {
  alabama: 'AL', alaska: 'AK', arizona: 'AZ', arkansas: 'AR', california: 'CA', colorado: 'CO', connecticut: 'CT', delaware: 'DE', florida: 'FL', georgia: 'GA', hawaii: 'HI', idaho: 'ID', illinois: 'IL', indiana: 'IN', iowa: 'IA', kansas: 'KS', kentucky: 'KY', louisiana: 'LA', maine: 'ME', maryland: 'MD', massachusetts: 'MA', michigan: 'MI', minnesota: 'MN', mississippi: 'MS', missouri: 'MO', montana: 'MT', nebraska: 'NE', nevada: 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', ohio: 'OH', oklahoma: 'OK', oregon: 'OR', pennsylvania: 'PA', 'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD', tennessee: 'TN', texas: 'TX', utah: 'UT', vermont: 'VT', virginia: 'VA', washington: 'WA', 'west virginia': 'WV', wisconsin: 'WI', wyoming: 'WY', 'district of columbia': 'DC', 'puerto rico': 'PR', guam: 'GU',
};

const countryLabels = new Set(['us', 'usa', 'u.s.', 'u.s.a.', 'united states', 'united states of america']);

function normalizeState(value: string | null | undefined) {
  const text = value?.trim();
  if (!text) return null;
  return stateCodes[text.toLowerCase()] || (text.length === 2 ? text.toUpperCase() : null);
}

function cleanCity(value: string) {
  const text = value
    .replace(/\s*~.*$/, '')
    .replace(/\s*\([A-Z0-9 -]{1,8}\)\s*$/i, '')
    .replace(/-(?:[A-Z]\d{1,4}|\d{1,4})$/i, '')
    .replace(/\s+/g, ' ')
    .replace(/^[,\s~-]+|[,\s~-]+$/g, '');
  if (!text) return null;
  return text === text.toUpperCase()
    ? text.toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
    : text;
}

export function normalizeLocation(item: LocationItem): string | null {
  const suppliedState = normalizeState(item.state);
  const suppliedCity = item.city ? cleanCity(item.city) : null;
  if (suppliedCity && suppliedState) return `${suppliedCity}, ${suppliedState}`;
  if (suppliedCity) return suppliedCity;

  const label = item.label?.trim();
  if (!label || /^(?:location not listed|not specified|n\/a)$/i.test(label)) return null;

  const ats = label.match(/^US-([A-Z]{2})-(.+)$/i);
  if (ats) {
    const city = cleanCity(ats[2]);
    return city ? `${city}, ${ats[1].toUpperCase()}` : null;
  }

  const workday = label.match(/^United States(?: of America)?-([^-]+)-(.+)$/i);
  if (workday) {
    const state = normalizeState(workday[1]);
    const city = cleanCity(workday[2]);
    if (city && state) return `${city}, ${state}`;
  }

  const tokens = label
    .replace(/\s*~.*$/, '')
    .split(/\s*[,|;]\s*/)
    .map((token) => token.trim())
    .filter((token) => token && !countryLabels.has(token.toLowerCase().replace(/\.$/, '')));
  for (let index = 0; index < tokens.length; index += 1) {
    const state = normalizeState(tokens[index]);
    if (!state) continue;
    const city = cleanCity(tokens[index - 1] || tokens[index + 1] || '');
    if (city) return `${city}, ${state}`;
  }

  const cleaned = cleanCity(label.replace(/,?\s*United States(?: of America)?/gi, ''));
  return cleaned && cleaned.length <= 70 ? cleaned : null;
}

export function summarizeLocations(items: LocationItem[] | null | undefined, fallback: string | null) {
  const candidates = items?.length ? items : [{ label: fallback, city: null, state: null, country: null, latitude: null, longitude: null }];
  const unique: string[] = [];
  const coordinates: { latitude: number; longitude: number }[] = [];
  const seen = new Set<string>();
  for (const item of candidates) {
    const normalized = normalizeLocation(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(normalized);
    const latitude = Number(item.latitude);
    const longitude = Number(item.longitude);
    if (Number.isFinite(latitude) && Number.isFinite(longitude)) coordinates.push({ latitude, longitude });
  }

  if (!unique.length) return { display: 'Location not listed', full: 'Location not listed', values: [], states: [], coordinates };
  const shown = unique.slice(0, 3);
  const remaining = unique.length - shown.length;
  const states = [...new Set(unique.flatMap((location) => {
    const match = location.match(/,\s*([A-Z]{2})$/);
    return match ? [match[1]] : [];
  }))];
  return {
    display: `${shown.join(' · ')}${remaining ? ` · +${remaining} more` : ''}`,
    full: unique.join(' · '),
    values: unique,
    states,
    coordinates,
  };
}
