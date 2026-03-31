import React, { useMemo } from 'react'
import MetricCard from '../components/MetricCard'
import AQIGauge from '../components/AQIGauge'
import AlarmPanel from '../components/AlarmPanel'
import { aqiColor, alarmColor } from '../utils/aqiColors'

export default function Overview({ data }) {
  const latest = useMemo(() => data[data.length - 1] ?? {}, [data])
  const maxAQI = useMemo(() => Math.max(...data.map(r => r.AQI_kalman ?? 0)), [data])

  return (
    <div>
      <div style={{ fontSize: '0.7rem', color: '#4b5563', marginBottom: '1.25rem', letterSpacing: '0.05em' }}>
        OVERVIEW — {data.length} samples loaded
      </div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <AQIGauge value={latest.AQI_kalman ?? 0} algorithm="kalman" />
        <AQIGauge value={latest.AQI_regression ?? 0} algorithm="regression" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <MetricCard label="CO (Kalman)" value={(latest.C_CO_kalman ?? 0).toFixed(2)} unit="ppm" color="#00d4ff" />
            <MetricCard label="NO₂ (Kalman)" value={(latest.C_NO2_kalman ?? 0).toFixed(1)} unit="ppb" color="#818cf8" />
            <MetricCard label="PM2.5 (Kalman)" value={(latest.PM_kalman ?? 0).toFixed(1)} unit="μg/m³" color="#34d399" />
          </div>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <MetricCard label="Temperature" value={(latest.T_adc ?? 0).toFixed(1)} unit="°C" color="#fb923c" />
            <MetricCard label="Humidity" value={(latest.RH_adc ?? 0).toFixed(1)} unit="%" color="#60a5fa" />
            <MetricCard label="Peak AQI" value={Math.round(maxAQI)} unit="" color={aqiColor(maxAQI)} sub="session maximum" />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <div className="card" style={{ flex: 1, minWidth: 200 }}>
          <div className="label" style={{ marginBottom: 10 }}>Alarm Distribution</div>
          {['NORMAL', 'WARNING', 'ALARM'].map(s => {
            const cnt = data.filter(r => r.alarm_state === s).length
            const pct = ((cnt / data.length) * 100).toFixed(1)
            return (
              <div key={s} style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', marginBottom: 3 }}>
                  <span style={{ color: alarmColor(s) }}>{s}</span>
                  <span style={{ color: '#6b7280' }}>{cnt} ({pct}%)</span>
                </div>
                <div style={{ height: 4, background: '#1f2937', borderRadius: 2 }}>
                  <div style={{ height: '100%', width: `${pct}%`, background: alarmColor(s), borderRadius: 2 }} />
                </div>
              </div>
            )
          })}
        </div>
        <div className="card" style={{ flex: 1, minWidth: 200 }}>
          <div className="label" style={{ marginBottom: 10 }}>Risk Score (latest)</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700, color: '#f59e0b', lineHeight: 1 }}>
            {(latest.risk_score_kalman ?? 0).toFixed(3)}
          </div>
          <div style={{ fontSize: '0.65rem', color: '#6b7280', marginTop: 6 }}>
            Composite: 0.35×CO + 0.35×NO₂ + 0.30×PM
          </div>
          <div style={{ fontSize: '0.65rem', color: '#4b5563', marginTop: 4 }}>
            Alarm triggers at R {'>'} 1.5
          </div>
        </div>
      </div>

      <AlarmPanel data={data} />
    </div>
  )
}
