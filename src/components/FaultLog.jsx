import React from 'react'

export default function FaultLog({ data }) {
  const faults = data
    .filter(r => r.fault_flags && r.fault_flags !== 'NONE')
    .slice(0, 80)

  return (
    <div className="card">
      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e5e7eb', marginBottom: '1rem' }}>
        FAULT LOG
        <span style={{ marginLeft: 12, fontSize: '0.65rem', color: faults.length > 0 ? '#ef4444' : '#10b981', fontWeight: 400 }}>
          {faults.length} events
        </span>
      </div>
      {faults.length === 0 ? (
        <div style={{ fontSize: '0.72rem', color: '#4b5563', padding: '1rem 0' }}>No faults detected in this scenario.</div>
      ) : (
        <div style={{ maxHeight: 320, overflowY: 'auto' }}>
          {faults.map((r, i) => (
            <div key={i} style={{ display: 'flex', gap: 16, padding: '5px 0', borderBottom: '1px solid #111827', fontSize: '0.68rem' }}>
              <span style={{ color: '#4b5563', minWidth: 60 }}>t={r.timestamp}s</span>
              <span style={{ color: '#ef4444' }}>{r.fault_flags}</span>
              <span style={{ color: '#6b7280', marginLeft: 'auto' }}>AQI {Math.round(r.AQI_kalman ?? 0)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
