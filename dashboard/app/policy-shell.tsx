import Link from 'next/link';
import type { ReactNode } from 'react';

export default function PolicyShell({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return (
    <main className="policy-page">
      <nav className="policy-nav"><Link className="brand" href="/"><span>AS</span>AeroScout</Link></nav>
      <article>
        <p className="eyebrow dark">{eyebrow}</p><h1>{title}</h1>{children}
      </article>
      <nav className="policy-links"><Link href="/">Internship finder</Link><Link href="/privacy">Privacy</Link><Link href="/terms">Terms</Link><Link href="/contact">Contact</Link></nav>
    </main>
  );
}
