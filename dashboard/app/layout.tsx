import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] });
const geistMono = Geist_Mono({ variable: '--font-geist-mono', subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AeroScout — Engineering & STEM Internship Finder',
  description: 'A focused dashboard for engineering and STEM internships across leading employers.',
  openGraph: {
    title: 'AeroScout — Engineering & STEM Internship Finder',
    description: 'Search current engineering and STEM internship opportunities.',
    images: ['https://aeroscout-internships.brendanlyons07.chatgpt.site/og.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AeroScout — Engineering & STEM Internship Finder',
    description: 'Search current engineering and STEM internship opportunities.',
    images: ['https://aeroscout-internships.brendanlyons07.chatgpt.site/og.png'],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className={`${geistSans.variable} ${geistMono.variable}`}>{children}</body></html>;
}
