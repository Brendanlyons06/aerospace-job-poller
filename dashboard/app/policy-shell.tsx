import type { ReactNode } from 'react';

/* eslint-disable @next/next/no-html-link-for-pages -- native navigation avoids the hosted router interception bug */

export default function PolicyShell({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return (
    <main className="policy-page">
      <nav className="policy-nav"><a className="brand" href="/"><span>AS</span>AeroScout</a></nav>
      <article>
        <p className="eyebrow dark">{eyebrow}</p><h1>{title}</h1>{children}
      </article>
      <nav className="policy-links"><a href="/">Internship finder</a><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/contact">Contact</a></nav>
    </main>
  );
}
