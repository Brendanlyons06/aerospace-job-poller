import ManageAlerts from '../manage-alerts';
import { getDashboardJobs } from '../../lib/jobs';

const labels: Record<string, string> = {
  'aerospace-defense': 'Aerospace & defense',
  'space-launch-spacecraft': 'Space & launch',
  'advanced-aircraft-autonomy': 'Aircraft & autonomy',
  'advanced-manufacturing-hardware': 'Manufacturing & hardware',
  'engineering-organization': 'Research & government',
  'other-engineering': 'Other engineering',
  gnc: 'GNC',
  'flight-controls': 'Flight controls',
  'flight-test': 'Flight test',
  'flight-sciences': 'Flight sciences',
  'aircraft-performance': 'Aircraft performance',
  'systems-integration-test': 'Systems integration & test',
  'mechanical-design': 'Mechanical design',
  'data-science': 'Data science & AI',
  'physics-research': 'Physics & research',
  'supply-chain': 'Supply chain',
};

function label(value: string) {
  return labels[value] || value.replace(/-/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default async function ManagePage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const [{ token = '' }, result] = await Promise.all([searchParams, getDashboardJobs()]);
  const disciplines = [...new Set(result.jobs.map((job) => job.discipline).filter((item): item is string => Boolean(item)))]
    .sort((a, b) => label(a).localeCompare(label(b)))
    .map((value) => ({ value, label: label(value) }));
  const sectors = [...new Set(result.jobs.map((job) => job.sector).filter((item): item is string => Boolean(item)))]
    .sort((a, b) => label(a).localeCompare(label(b)))
    .map((value) => ({ value, label: label(value) }));
  const companies = [...new Set(result.jobs.map((job) => job.company))].sort();
  const states = [...new Set(result.jobs.flatMap((job) => job.locationStates))].sort();
  return <main className="action-page"><ManageAlerts token={token} disciplines={disciplines} sectors={sectors} companies={companies} states={states} /></main>;
}
