'use client';

import React from 'react';

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div style={{ padding: '2rem', backgroundColor: '#450a0a', border: '1px solid #991b1b', borderRadius: '0.5rem', color: '#fca5a5' }}>
      <h2>System Exception Encountered</h2>
      <p style={{ fontFamily: 'monospace' }}>{error.message || 'An unexpected error occurred in the web application layer.'}</p>
      <button
        onClick={() => reset()}
        style={{ padding: '0.5rem 1rem', backgroundColor: '#dc2626', color: '#ffffff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer' }}
      >
        Retry Action
      </button>
    </div>
  );
}
