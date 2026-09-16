import React from 'react';

export default function HomePage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
        <h2 style={{ marginTop: 0, color: '#f8fafc', fontSize: '1.5rem' }}>Platform Application Foundation</h2>
        <p style={{ color: '#94a3b8', lineHeight: '1.6' }}>
          This system foundation establishes the web application, API boundaries, FastAPI Python ML service integration,
          shared contracts, and architectural controls according to the approved Stage 2 Architecture Specifications.
        </p>
        <div style={{ display: 'inline-block', padding: '0.25rem 0.75rem', backgroundColor: '#0284c7', borderRadius: '0.25rem', fontSize: '0.875rem', fontWeight: 600 }}>
          Stage 3 — Application Skeleton Established
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#38bdf8' }}>Web & API Gateway Boundary</h3>
          <p style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Next.js App Router (TypeScript)</p>
          <ul style={{ paddingLeft: '1.25rem', color: '#94a3b8', fontSize: '0.875rem', lineHeight: '1.5' }}>
            <li>App Router Foundation</li>
            <li>Strict TypeScript Configuration</li>
            <li>Correlation ID Tracking</li>
            <li>Structured API Responses</li>
          </ul>
        </div>

        <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#38bdf8' }}>Python ML Service Boundary</h3>
          <p style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>FastAPI + Pydantic (Python 3.12)</p>
          <ul style={{ paddingLeft: '1.25rem', color: '#94a3b8', fontSize: '0.875rem', lineHeight: '1.5' }}>
            <li>Typed Contract Schemas</li>
            <li>Async Task Execution Boundary</li>
            <li>Zero-Leakage Feature Pipeline Boundary</li>
            <li>First-Class NO-BET Abstention Engine</li>
          </ul>
        </div>

        <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#38bdf8' }}>Architectural Directives</h3>
          <p style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Strict Anti-Fabrication Rules</p>
          <ul style={{ paddingLeft: '1.25rem', color: '#94a3b8', fontSize: '0.875rem', lineHeight: '1.5' }}>
            <li>No Synthetic / Fake Predictions</li>
            <li>No Fabricated Football Statistics</li>
            <li>No LLM Probability Generation</li>
            <li>Immutable Audit Trail Logging</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
