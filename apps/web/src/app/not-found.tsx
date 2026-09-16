import React from 'react';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div style={{ padding: '3rem', textAlign: 'center', backgroundColor: '#1e293b', borderRadius: '0.5rem' }}>
      <h2 style={{ fontSize: '2rem', color: '#f8fafc' }}>404 — Resource Not Found</h2>
      <p style={{ color: '#94a3b8' }}>The requested page or resource does not exist on this server.</p>
      <Link href="/" style={{ color: '#38bdf8', textDecoration: 'underline' }}>Return to Home Page</Link>
    </div>
  );
}
