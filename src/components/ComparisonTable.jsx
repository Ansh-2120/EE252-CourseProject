import React from 'react'

export default function ComparisonTable({ metrics }) {
  if (!metrics || metrics.length === 0) return null

  const rows = [
    { label: 'CO RMSE (ppm)',     k: 'RMSE_CO_kalman',   r: 'RMSE_CO_regression'  },
    { label: 'NO2 RMSE (ppb)',    k: 'RMSE_NO2_kalman',  r: 'RMSE_NO2_regression' },
    { label: 'PM RMSE (μg/m³)',   k: 'RMSE_PM_kalman',   r: 'RMSE_PM_regression'  },
    { label: 'CO MAE (ppm)',      k: 'MAE_CO_kalman',    r: 'MAE_CO_regression'   },
    { label: 'NO2 MAE (ppb)',     k: 'MAE_NO2_kalman',   r: 'MAE_NO2_regression'  },
    { label: 'PM MAE (μg/m³)',    k: 'MAE_PM_kalman',    r: 'MAE_PM_regression'   },
  ]

  const th = { padding: '6px 12px', textAlign: 'left', fontSize: '0.65rem', letterSpacing: '0.1em', color: '#6b7280', borderBottom: '1px solid #1f2937', textTransform: 'uppercase' }
  const td = { padding: '6px 12px', fontSize: '0.72rem', borderBottom: '1px solid #111827' }

  return (
    <div className="card">
      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e5e7eb', marginBottom: '1rem' }}>ALGORITHM COMPARISON — RMSE / MAE</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={th}>Metric</th>
              {metrics.map(m => <th key={m.scenario} style={{ ...th, textAlign: 'center' }}>{m.scenario}</th>)}
              <th style={{ ...th, textAlign: 'center', color: '#00d4ff' }}>Kalman</th>
              <th style={{ ...th, textAlign: 'center', color: '#f59e0b' }}>Regression</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => {
              const vals = metrics.map(m => ({ k: parseFloat(m[row.k]) || 0, r: parseFloat(m[row.r]) || 0 }))
              const avgK = vals.reduce((a, v) => a + v.k, 0) / vals.length
              const avgR = vals.reduce((a, v) => a + v.r, 0) / vals.length
              const kWins = avgK < avgR
              return (
                <tr key={row.label} style={{ background: '#0a0e1a' }}>
                  <td style={{ ...td, color: '#9ca3af' }}>{row.label}</td>
                  {vals.map((v, i) => (
                    <td key={i} style={{ ...td, textAlign: 'center', color: '#6b7280', fontSize: '0.65rem' }}>
                      <span style={{ color: '#00d4ff' }}>{v.k.toFixed(3)}</span>
                      {' / '}
                      <span style={{ color: '#f59e0b' }}>{v.r.toFixed(3)}</span>
                    </td>
                  ))}
                  <td style={{ ...td, textAlign: 'center', color: kWins ? '#10b981' : '#6b7280', fontWeight: kWins ? 600 : 400 }}>{avgK.toFixed(3)}</td>
                  <td style={{ ...td, textAlign: 'center', color: !kWins ? '#10b981' : '#6b7280', fontWeight: !kWins ? 600 : 400 }}>{avgR.toFixed(3)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: '0.75rem', fontSize: '0.62rem', color: '#4b5563' }}>
        Green = lower error (better). Each cell: Kalman / Regression per scenario.
      </div>
    </div>
  )
}
