import React from 'react';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>Football AI Intelligence — Private Beta Console</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body style={{ margin: 0, padding: 0, fontFamily: 'system-ui, -apple-system, sans-serif', backgroundColor: '#0f172a', color: '#f8fafc' }}>
        <header style={{ backgroundColor: '#1e293b', borderBottom: '1px solid #334155', padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h1 style={{ margin: 0, fontSize: '1.25rem', color: '#38bdf8' }}>Football AI Intelligence</h1>
            <span style={{ backgroundColor: '#0284c7', color: '#ffffff', padding: '0.2rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem', fontWeight: 600 }}>PRIVATE BETA</span>
          </div>
          <nav style={{ display: 'flex', gap: '1.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
            <Link href="/" style={{ color: '#f8fafc', textDecoration: 'none' }}>Dashboard</Link>
            <Link href="/predict" style={{ color: '#cbd5e1', textDecoration: 'none' }}>Generate Prediction</Link>
            <Link href="/history" style={{ color: '#cbd5e1', textDecoration: 'none' }}>Prediction History</Link>
            <Link href="/status" style={{ color: '#cbd5e1', textDecoration: 'none' }}>System Health</Link>
          </nav>
        </header>

        <main style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1rem' }}>
          {children}
        </main>

        <footer style={{ borderTop: '1px solid #1e293b', padding: '1.5rem', textAlign: 'center', color: '#64748b', fontSize: '0.85rem', marginTop: '4rem' }}>
          Football AI Platform — Stage 25 Controlled Private Beta. Strict Anti-Odds & Anti-Fabrication Architecture.
        </footer>
      </body>
    </html>
  );
}
