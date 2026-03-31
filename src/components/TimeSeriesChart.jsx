import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function TimeSeriesChart({ data, lines, title, unit, height = 260 }) {
  const sampled = data.filter((_, i) => i % Math.max(1, Math.floor(data.length / 400)) === 0)

  return (
    <div className="card" style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e5e7eb', letterSpacing: '0.05em' }}>{title}</span>
        <span className="label">{unit}</span>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={sampled} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="timestamp" tick={{ fill: '#4b5563', fontSize: 10 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} label={{ value: 'time (s)', fill: '#4b5563', fontSize: 9, position: 'insideBottomRight', offset: -4 }} />
          <YAxis tick={{ fill: '#4b5563', fontSize: 10 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
          <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 6, fontSize: '0.7rem', fontFamily: 'JetBrains Mono' }} />
          <Legend wrapperStyle={{ fontSize: '0.65rem', paddingTop: 8 }} />
          {lines.map(l => (
            <Line key={l.key} type="monotone" dataKey={l.key} stroke={l.color} dot={false} strokeWidth={l.width ?? 1.5} name={l.name} strokeDasharray={l.dash} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
