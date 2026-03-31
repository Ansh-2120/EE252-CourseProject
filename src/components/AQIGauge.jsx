import React from 'react'
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts'
import { aqiColor, aqiLabel } from '../utils/aqiColors'

export default function AQIGauge({ value = 0, algorithm = 'kalman' }) {
  const pct  = Math.min(value / 500, 1)
  const col  = aqiColor(value)
  const data = [{ value: pct * 100, fill: col }]

  return (
    <div className="card" style={{ textAlign: 'center', minWidth: 200 }}>
      <div className="label" style={{ marginBottom: 8 }}>AQI — {algorithm.toUpperCase()}</div>
      <div style={{ position: 'relative', height: 160 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart cx="50%" cy="80%" innerRadius="70%" outerRadius="100%" startAngle={180} endAngle={0} data={data} barSize={14}>
            <RadialBar dataKey="value" cornerRadius={6} background={{ fill: '#1f2937' }} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div style={{ position: 'absolute', bottom: 10, left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: col, lineHeight: 1 }}>{Math.round(value)}</div>
          <div style={{ fontSize: '0.62rem', color: '#6b7280', marginTop: 2 }}>{aqiLabel(value)}</div>
        </div>
      </div>
    </div>
  )
}
