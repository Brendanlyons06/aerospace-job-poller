import SubscriptionAction from '../subscription-action';

export default async function UnsubscribePage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const { token = '' } = await searchParams;
  return <main className="action-page"><SubscriptionAction mode="unsubscribe" token={token} /></main>;
}
