import React from 'react';
import Link from 'next/link';

export const metadata = {
  title: 'Football AI Intelligence & ML Platform',
  description: 'Production-oriented Football AI Intelligence & Machine-Learning Platform Foundation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'system-ui, -apple-system, sans-serif', backgroundColor: '#0f172a', color: '#f8fafc' }}>
        <header style={{ padding: '1rem 2rem', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.25rem', margin: 0, fontWeight: 600, color: '#38bdf8' }}>
            Football AI Platform — Stage 3 Foundation
          </h1>
          <nav style={{ display: 'flex', gap: '1.5rem' }}>
            <Link href="/" style={{ color: '#94a3b8', textDecoration: 'none' }}>System Status</Link>
            <Link href="/api/v1/health" style={{ color: '#94a3b8', textDecoration: 'none' }}>API Health</Link>
            <Link href="/api/v1/readiness" style={{ color: '#94a3b8', textDecoration: 'none' }}>API Readiness</Link>
          </nav>
        </header>
        <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
