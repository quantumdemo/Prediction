'use client';

import React, { useState } from 'react';

export default function PredictPage() {
  const [homeTeam, setHomeTeam] = useState('Arsenal');
  const [awayTeam, setAwayTeam] = useState('Chelsea');
  const [matchDate, setMatchDate] = useState('2026-03-15');
  const [competition, setCompetition] = useState('COMP_ENG_PL');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    try {
      const payload = {
        fixture_id: `FIX_BETA_${homeTeam.toUpperCase().replace(/\s+/g, '')}_${awayTeam.toUpperCase().replace(/\s+/g, '')}`,
        home_team: homeTeam,
        away_team: awayTeam,
        competition: competition,
        season: '2025_2026',
        match_date: matchDate,
        kickoff_time: '15:00',
        venue: 'Canonical Stadium',
        base_features: {
          rolling_home_goals_for_5: 2.1,
          rolling_away_goals_against_5: 1.2,
          rest_days_difference: 1.0,
        },
        raw_research_inputs: [
          {
            category: 'INJURIES',
            entity: homeTeam,
            claim: 'Key midfielder fully recovered',
            source_domain: 'skysports.com',
            source_url: 'https://skysports.com/news/12345',
            research_state: 'VERIFIED',
          },
        ],
      };

      const response = await fetch(`${apiBase}/api/v1/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-correlation-id': `beta-ui-${Date.now()}` },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (response.status === 503 || response.status === 500) {
          throw new Error(`INFRASTRUCTURE_FAILURE (HTTP ${response.status}): Database or backend service unavailable.`);
        }
        const errJson = (await response.json().catch(() => ({}))) as { error?: { message?: string } };
        throw new Error(errJson.error?.message || `API error HTTP ${response.status}`);
      }

      const data = (await response.json()) as Record<string, unknown>;
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect to backend prediction service.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ELIGIBLE':
        return <span style={{ backgroundColor: '#166534', color: '#86efac', padding: '0.4rem 0.8rem', borderRadius: '0.25rem', fontWeight: 700, fontSize: '0.9rem' }}>PREDICTION (ELIGIBLE)</span>;
      case 'LOW_CONFIDENCE':
      case 'HIGH_RISK':
      case 'INSUFFICIENT_EVIDENCE':
      case 'NO_BET':
        return <span style={{ backgroundColor: '#854d0e', color: '#fde047', padding: '0.4rem 0.8rem', borderRadius: '0.25rem', fontWeight: 700, fontSize: '0.9rem' }}>NO BET ({status})</span>;
      case 'BLOCKED':
      case 'BLOCKED_NO_FORECAST':
        return <span style={{ backgroundColor: '#991b1b', color: '#fca5a5', padding: '0.4rem 0.8rem', borderRadius: '0.25rem', fontWeight: 700, fontSize: '0.9rem' }}>BLOCKED ({status})</span>;
      default:
        return <span style={{ backgroundColor: '#374151', color: '#d1d5db', padding: '0.4rem 0.8rem', borderRadius: '0.25rem', fontWeight: 700, fontSize: '0.9rem' }}>{status}</span>;
    }
  };

  const forecastSummary = result?.forecast_summary as { probabilities_1x2?: { home?: number; draw?: number; away?: number } } | undefined;
  const fixtureSummary = result?.fixture_summary as { home_team?: string; away_team?: string } | undefined;
  const modelAttr = result?.model_attribution as { model_name?: string; calibration_method?: string } | undefined;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
        <h2 style={{ marginTop: 0, color: '#f8fafc', fontSize: '1.25rem' }}>Generate Match Prediction</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Execute the 9-stage prediction integration pipeline against the production <code style={{ color: '#38bdf8' }}>xgboost_platt</code> forecaster.
        </p>

        <form onSubmit={handlePredict} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.25rem' }}>Home Team</label>
            <input type="text" value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)} required style={{ width: '100%', padding: '0.5rem', backgroundColor: '#0f172a', border: '1px solid #334155', color: '#fff', borderRadius: '0.25rem' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.25rem' }}>Away Team</label>
            <input type="text" value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)} required style={{ width: '100%', padding: '0.5rem', backgroundColor: '#0f172a', border: '1px solid #334155', color: '#fff', borderRadius: '0.25rem' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.25rem' }}>Match Date</label>
            <input type="date" value={matchDate} onChange={(e) => setMatchDate(e.target.value)} required style={{ width: '100%', padding: '0.5rem', backgroundColor: '#0f172a', border: '1px solid #334155', color: '#fff', borderRadius: '0.25rem' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.25rem' }}>Competition</label>
            <input type="text" value={competition} onChange={(e) => setCompetition(e.target.value)} required style={{ width: '100%', padding: '0.5rem', backgroundColor: '#0f172a', border: '1px solid #334155', color: '#fff', borderRadius: '0.25rem' }} />
          </div>

          <div style={{ gridColumn: '1 / -1', marginTop: '0.5rem' }}>
            <button type="submit" disabled={loading} style={{ padding: '0.6rem 1.5rem', backgroundColor: loading ? '#475569' : '#0284c7', color: '#fff', border: 'none', borderRadius: '0.25rem', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}>
              {loading ? 'Executing Pipeline...' : 'Generate Prediction'}
            </button>
          </div>
        </form>
      </section>

      {error && (
        <div style={{ backgroundColor: '#450a0a', border: '1px solid #991b1b', color: '#fca5a5', padding: '1rem', borderRadius: '0.5rem' }}>
          <strong style={{ display: 'block', marginBottom: '0.25rem' }}>SYSTEM / INFRASTRUCTURE ERROR</strong>
          <span>{error}</span>
        </div>
      )}

      {result && (
        <section style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '1rem', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#f8fafc' }}>
                {fixtureSummary?.home_team || homeTeam} vs {fixtureSummary?.away_team || awayTeam}
              </h3>
              <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Report ID: {String(result.report_id || '')} | Audit Hash: {String(result.audit_hash || '').slice(0, 12)}...</span>
            </div>
            <div>{getStatusBadge(String(result.decision_status || 'UNKNOWN'))}</div>
          </div>

          {forecastSummary && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ color: '#38bdf8', marginTop: 0 }}>1X2 Calibrated Probabilities</h4>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ backgroundColor: '#0f172a', padding: '0.75rem 1.25rem', borderRadius: '0.25rem', textAlign: 'center', flex: 1 }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Home Win</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>{((forecastSummary.probabilities_1x2?.home || 0) * 100).toFixed(1)}%</div>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '0.75rem 1.25rem', borderRadius: '0.25rem', textAlign: 'center', flex: 1 }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Draw</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>{((forecastSummary.probabilities_1x2?.draw || 0) * 100).toFixed(1)}%</div>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '0.75rem 1.25rem', borderRadius: '0.25rem', textAlign: 'center', flex: 1 }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Away Win</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>{((forecastSummary.probabilities_1x2?.away || 0) * 100).toFixed(1)}%</div>
                </div>
              </div>
            </div>
          )}

          <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
            <strong>Model Attribution:</strong> {modelAttr?.model_name} ({modelAttr?.calibration_method})
          </div>
        </section>
      )}
    </div>
  );
}
