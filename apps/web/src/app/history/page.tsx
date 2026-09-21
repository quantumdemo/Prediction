'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface ReportItem {
  report_id: string;
  prediction_id: string;
  fixture_id: string;
  model_name: string;
  calibration_method: string;
  audit_hash: string;
  final_decision_status: string;
}

export default function HistoryPage() {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHistory() {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? '';
      try {
        const response = await fetch(`${apiBase}/api/v1/history?limit=20`, {
          headers: { 'x-correlation-id': `history-ui-${Date.now()}` },
        });

        if (!response.ok) {
          throw new Error(`Failed to load prediction history (HTTP ${response.status})`);
        }

        const data = (await response.json()) as { reports?: ReportItem[] };
        setReports(data.reports || []);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Error connecting to prediction history repository.';
        setError(msg);
      } finally {
        setLoading(false);
      }
    }

    fetchHistory();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
        <h2 style={{ marginTop: 0, color: '#f8fafc', fontSize: '1.25rem' }}>Auditable Prediction History</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Historical prediction reports persisted immutably in PostgreSQL with SHA256 audit hashes and complete prediction chain provenance.
        </p>
      </section>

      {loading && (
        <div style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', textAlign: 'center', color: '#94a3b8' }}>
          Loading prediction history records...
        </div>
      )}

      {error && (
        <div style={{ backgroundColor: '#450a0a', border: '1px solid #991b1b', color: '#fca5a5', padding: '1rem', borderRadius: '0.5rem' }}>
          <strong style={{ display: 'block', marginBottom: '0.25rem' }}>SYSTEM ERROR</strong>
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && reports.length === 0 && (
        <div style={{ backgroundColor: '#1e293b', padding: '2rem', borderRadius: '0.5rem', textAlign: 'center', color: '#94a3b8', border: '1px solid #334155' }}>
          <h3 style={{ marginTop: 0, color: '#f8fafc' }}>No Prediction Reports Found</h3>
          <p>Generate a match prediction from the <Link href="/predict" style={{ color: '#38bdf8' }}>Generate Prediction</Link> tab to persist reports.</p>
        </div>
      )}

      {!loading && reports.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {reports.map((rep) => (
            <div key={rep.report_id} style={{ backgroundColor: '#1e293b', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4 style={{ margin: 0, color: '#f8fafc', fontSize: '1rem' }}>Fixture ID: {rep.fixture_id}</h4>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                  Report ID: {rep.report_id} | Model: {rep.model_name} ({rep.calibration_method})
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                  Audit Hash: {rep.audit_hash}
                </div>
              </div>

              <div>
                <span style={{ backgroundColor: rep.final_decision_status === 'ELIGIBLE' ? '#166534' : '#854d0e', color: '#fff', padding: '0.3rem 0.6rem', borderRadius: '0.25rem', fontSize: '0.8rem', fontWeight: 600 }}>
                  {rep.final_decision_status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
