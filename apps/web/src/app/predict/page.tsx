'use client';

import React, { useState, useEffect } from 'react';

// Competition format map and team auto-completion inference
const COMMON_COMPETITIONS = [
  { code: 'COMP_ENG_PL', label: 'English Premier League (COMP_ENG_PL)' },
  { code: 'COMP_ESP_LL', label: 'Spanish La Liga (COMP_ESP_LL)' },
  { code: 'COMP_GER_BL', label: 'German Bundesliga (COMP_GER_BL)' },
  { code: 'COMP_ITA_SA', label: 'Italian Serie A (COMP_ITA_SA)' },
  { code: 'COMP_FRA_L1', label: 'French Ligue 1 (COMP_FRA_L1)' },
  { code: 'COMP_UEFA_CL', label: 'UEFA Champions League (COMP_UEFA_CL)' },
];

const KNOWN_TEAM_COMPETITION_MAP: Record<string, string> = {
  // English Premier League
  arsenal: 'COMP_ENG_PL',
  chelsea: 'COMP_ENG_PL',
  liverpool: 'COMP_ENG_PL',
  manchesterunited: 'COMP_ENG_PL',
  manchestercity: 'COMP_ENG_PL',
  tottenham: 'COMP_ENG_PL',
  astonvilla: 'COMP_ENG_PL',
  newcastle: 'COMP_ENG_PL',
  // La Liga
  realmadrid: 'COMP_ESP_LL',
  barcelona: 'COMP_ESP_LL',
  atleticomadrid: 'COMP_ESP_LL',
  sevilla: 'COMP_ESP_LL',
  // Bundesliga
  bayernmunich: 'COMP_GER_BL',
  borussiadortmund: 'COMP_GER_BL',
  bayerleverkusen: 'COMP_GER_BL',
  // Serie A
  intermilan: 'COMP_ITA_SA',
  acmilan: 'COMP_ITA_SA',
  juventus: 'COMP_ITA_SA',
  napoli: 'COMP_ITA_SA',
};

export default function PredictPage() {
  const [homeTeam, setHomeTeam] = useState('Arsenal');
  const [awayTeam, setAwayTeam] = useState('Chelsea');
  const [matchDate, setMatchDate] = useState('2026-03-15');
  const [competition, setCompetition] = useState('COMP_ENG_PL');
  const [autoFilled, setAutoFilled] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-completion logic: automatically infers competition code when teams or match date change
  useEffect(() => {
    const normHome = homeTeam.toLowerCase().replace(/[^a-z0-9]/g, '');
    const normAway = awayTeam.toLowerCase().replace(/[^a-z0-9]/g, '');

    const inferredComp = KNOWN_TEAM_COMPETITION_MAP[normHome] || KNOWN_TEAM_COMPETITION_MAP[normAway];
    if (inferredComp) {
      setCompetition(inferredComp);
      setAutoFilled(true);
    } else {
      setAutoFilled(false);
    }
  }, [homeTeam, awayTeam, matchDate]);

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
          Execute the 9-stage prediction integration pipeline against the production <code style={{ color: '#38bdf8' }}>xgboost_platt</code> forecaster. Competition codes follow the canonical format <code style={{ color: '#38bdf8' }}>COMP_&lt;NATION&gt;_&lt;LEAGUE&gt;</code> (e.g. <code style={{ color: '#38bdf8' }}>COMP_ENG_PL</code>) and auto-complete based on team names.
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
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.25rem' }}>
              Competition Code {autoFilled && <span style={{ color: '#38bdf8', fontSize: '0.75rem', fontWeight: 600 }}>(Auto-completed)</span>}
            </label>
            <select
              value={competition}
              onChange={(e) => {
                setCompetition(e.target.value);
                setAutoFilled(false);
              }}
              style={{ width: '100%', padding: '0.5rem', backgroundColor: '#0f172a', border: '1px solid #334155', color: '#fff', borderRadius: '0.25rem' }}
            >
              {COMMON_COMPETITIONS.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.label}
                </option>
              ))}
            </select>
            <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem', display: 'block' }}>Format: COMP_&lt;COUNTRY&gt;_&lt;LEAGUE&gt;</span>
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
