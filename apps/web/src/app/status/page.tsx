'use client';

import React, { useEffect, useState } from 'react';

interface HealthData {
  data?: {
    status?: string;
    service?: string;
    environment?: string;
    version?: string;
  };
}

interface ReadinessData {
  data?: {
    status?: string;
    checks?: {
      database?: string;
      environment?: string;
    };
  };
}

export default function StatusPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [readiness, setReadiness] = useState<ReadinessData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSystemStatus() {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      try {
        const [hRes, rRes] = await Promise.all([
          fetch(`${apiBase}/api/v1/health`, { headers: { 'x-correlation-id': `health-ui-${Date.now()}` } }),
          fetch(`${apiBase}/api/v1/readiness`, { headers: { 'x-correlation-id': `readiness-ui-${Date.now()}` } }),
        ]);

        if (hRes.ok) {
          setHealth((await hRes.json()) as HealthData);
        }
        if (rRes.ok) {
          setReadiness((await rRes.json()) as ReadinessData);
        } else {
          setReadiness({ data: { status: 'NOT_READY', checks: { database: 'UNREACHABLE' } } });
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Error connecting to backend health services.';
        setError(msg);
      } finally {
        setLoading(false);
      }
    }

    fetchSystemStatus();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
        <h2 style={{ marginTop: 0, color: '#f8fafc', fontSize: '1.25rem' }}>System Operational Health & Readiness</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Real-time health telemetry from FastAPI Python ML service boundary and PostgreSQL database connection boundary.
        </p>
      </section>

      {loading && (
        <div style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', textAlign: 'center', color: '#94a3b8' }}>
          Checking system health and readiness...
        </div>
      )}

      {error && (
        <div style={{ backgroundColor: '#450a0a', border: '1px solid #991b1b', color: '#fca5a5', padding: '1rem', borderRadius: '0.5rem' }}>
          <strong style={{ display: 'block', marginBottom: '0.25rem' }}>SYSTEM UNREACHABLE</strong>
          <span>{error}</span>
        </div>
      )}

      {!loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
          <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
            <h3 style={{ marginTop: 0, color: '#38bdf8', fontSize: '1.1rem' }}>FastAPI ML Service Health</h3>
            <div style={{ marginTop: '0.75rem' }}>
              <span style={{ backgroundColor: health?.data?.status === 'HEALTHY' ? '#166534' : '#854d0e', color: '#fff', padding: '0.3rem 0.6rem', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: 600 }}>
                {health?.data?.status || 'UNKNOWN'}
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.75rem', lineHeight: '1.6' }}>
              <div>Service: {health?.data?.service || 'ml-service'}</div>
              <div>Environment: {health?.data?.environment || 'development'}</div>
              <div>Version: {health?.data?.version || '0.1.0'}</div>
            </div>
          </div>

          <div style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
            <h3 style={{ marginTop: 0, color: '#38bdf8', fontSize: '1.1rem' }}>PostgreSQL Database Readiness</h3>
            <div style={{ marginTop: '0.75rem' }}>
              <span style={{ backgroundColor: readiness?.data?.status === 'READY' ? '#166534' : '#991b1b', color: '#fff', padding: '0.3rem 0.6rem', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: 600 }}>
                {readiness?.data?.status || 'NOT_READY'}
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.75rem', lineHeight: '1.6' }}>
              <div>Database Connection: {readiness?.data?.checks?.database || 'UNHEALTHY'}</div>
              <div>Environment Check: {readiness?.data?.checks?.environment || 'OK'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
