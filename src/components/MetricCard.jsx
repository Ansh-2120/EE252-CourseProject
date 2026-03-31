import React from 'react'

export default function MetricCard({ label, value, unit, color = '#00d4ff', sub }) {
  return (
    <div className="card" style={{ minWidth: 140 }}>
      <div className="label" style={{ marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: '1.6rem', fontWeight: 700, color, lineHeight: 1 }}>
        {value ?? '—'}
        <span style={{ fontSize: '0.7rem', fontWeight: 400, color: '#6b7280', marginLeft: 4 }}>{unit}</span>
      </div>
      {sub && <div style={{ fontSize: '0.65rem', color: '#6b7280', marginTop: 6 }}>{sub}</div>}
    </div>
  )
}
