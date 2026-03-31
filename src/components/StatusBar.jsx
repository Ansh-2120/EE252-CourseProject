import React from 'react'
import { alarmColor, aqiColor, aqiLabel } from '../utils/aqiColors'

export default function StatusBar({ latest }) {
  if (!latest) return null
  const alarm = latest.alarm_state
  const aqi   = Math.round(latest.AQI_kalman ?? 0)
  const fault = latest.fault_flags

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '0.6rem 1.5rem', background: '#0d1117', borderBottom: '1px solid #1f2937', fontSize: '0.7rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: alarmColor(alarm), boxShadow: `0 0 6px ${alarmColor(alarm)}` }} />
        <span style={{ color: alarmColor(alarm), fontWeight: 600, letterSpacing: '0.1em' }}>{alarm}</span>
      </div>
      <div style={{ color: '#1f2937' }}>|</div>
      <div style={{ color: '#6b7280' }}>AQI <span style={{ color: aqiColor(aqi), fontWeight: 600 }}>{aqi}</span> — {aqiLabel(aqi)}</div>
      <div style={{ color: '#1f2937' }}>|</div>
      <div style={{ color: fault === 'NONE' ? '#6b7280' : '#ef4444' }}>
        {fault === 'NONE' ? 'No Faults' : `⚠ ${fault}`}
      </div>
      <div style={{ marginLeft: 'auto', color: '#374151' }}>t = {latest.timestamp}s</div>
    </div>
  )
}
