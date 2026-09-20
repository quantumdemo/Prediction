import React from 'react';

export default function DashboardPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
        <h2 style={{ marginTop: 0, color: '#f8fafc', fontSize: '1.5rem' }}>Private Beta Operational Dashboard</h2>
        <p style={{ color: '#94a3b8', lineHeight: '1.6' }}>
          Welcome to the Football AI Platform Private Beta Console. This system evaluates real football match features, validates web research claims, executes probability calibration via <code style={{ color: '#38bdf8' }}>xgboost_platt</code>, and outputs auditable prediction reports with first-class <code style={{ color: '#f59e0b' }}>NO BET</code> and <code style={{ color: '#ef4444' }}>BLOCKED</code> risk handling.
        </p>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
        <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#38bdf8', fontSize: '1.1rem' }}>Generate Prediction</h3>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8', lineHeight: '1.5' }}>
            Run the 9-step production inference pipeline for an upcoming match fixture with pre-match research facts.
          </p>
          <a href="/predict" style={{ display: 'inline-block', marginTop: '0.5rem', padding: '0.5rem 1rem', backgroundColor: '#0284c7', color: '#fff', borderRadius: '0.25rem', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
            Launch Pipeline &rarr;
          </a>
        </div>

        <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#38bdf8', fontSize: '1.1rem' }}>Prediction History</h3>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8', lineHeight: '1.5' }}>
            Inspect auditable historical prediction reports, SHA256 audit hashes, and full provenance chains.
          </p>
          <a href="/history" style={{ display: 'inline-block', marginTop: '0.5rem', padding: '0.5rem 1rem', backgroundColor: '#334155', color: '#fff', borderRadius: '0.25rem', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
            View History &rarr;
          </a>
        </div>

        <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#38bdf8', fontSize: '1.1rem' }}>System Health & Readiness</h3>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8', lineHeight: '1.5' }}>
            Monitor live PostgreSQL database connectivity, connection pooling, and FastAPI service readiness.
          </p>
          <a href="/status" style={{ display: 'inline-block', marginTop: '0.5rem', padding: '0.5rem 1rem', backgroundColor: '#334155', color: '#fff', borderRadius: '0.25rem', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
            Check Health &rarr;
          </a>
        </div>
      </div>

      <section style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
        <h3 style={{ marginTop: 0, color: '#f8fafc', fontSize: '1.1rem' }}>System Decision Status Legend</h3>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          <span style={{ backgroundColor: '#166534', color: '#86efac', padding: '0.3rem 0.75rem', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: 'bold' }}>PREDICTION (ELIGIBLE)</span>
          <span style={{ backgroundColor: '#854d0e', color: '#fde047', padding: '0.3rem 0.75rem', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: 'bold' }}>NO BET (LOW CONFIDENCE / HIGH RISK)</span>
          <span style={{ backgroundColor: '#991b1b', color: '#fca5a5', padding: '0.3rem 0.75rem', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: 'bold' }}>BLOCKED (EVIDENCE CONFLICT / UNVERIFIED)</span>
          <span style={{ backgroundColor: '#374151', color: '#d1d5db', padding: '0.3rem 0.75rem', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: 'bold' }}>SYSTEM / INFRASTRUCTURE ERROR</span>
        </div>
      </section>
    </div>
  );
}
