import React from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { alarmColor } from '../utils/aqiColors'

const stateToNum = s => s === 'ALARM' ? 2 : s === 'WARNING' ? 1 : 0

export default function AlarmPanel({ data }) {
  const sampled = data
    .filter((_, i) => i % Math.max(1, Math.floor(data.length / 400)) === 0)
    .map(r => ({ t: r.timestamp, state: stateToNum(r.alarm_state), aqi: r.AQI_kalman ?? 0 }))

  const counts = { NORMAL: 0, WARNING: 0, ALARM: 0 }
  data.forEach(r => { if (counts[r.alarm_state] !== undefined) counts[r.alarm_state]++ })

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e5e7eb' }}>ALARM STATE TIMELINE</span>
        <div style={{ display: 'flex', gap: 12, fontSize: '0.65rem' }}>
          {Object.entries(counts).map(([k, v]) => (
            <span key={k} style={{ color: alarmColor(k) }}>{k}: {v}</span>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={sampled} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="aqi" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#00d4ff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="t" tick={{ fill: '#4b5563', fontSize: 10 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
          <YAxis tick={{ fill: '#4b5563', fontSize: 10 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} domain={[0, 500]} />
          <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1f2937', fontSize: '0.7rem', fontFamily: 'JetBrains Mono' }} formatter={(v, n) => [Math.round(v), n]} />
          <Area type="monotone" dataKey="aqi" stroke="#00d4ff" fill="url(#aqi)" strokeWidth={1.5} name="AQI" dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
