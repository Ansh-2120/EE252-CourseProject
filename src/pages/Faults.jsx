import React from 'react'
import FaultLog from '../components/FaultLog'
import AlarmPanel from '../components/AlarmPanel'
import TimeSeriesChart from '../components/TimeSeriesChart'
import MetricCard from '../components/MetricCard'
import { alarmColor } from '../utils/aqiColors'

export default function Faults({ data }) {
  const faultCount  = data.filter(r => r.fault_flags !== 'NONE').length
  const alarmCount  = data.filter(r => r.alarm_state === 'ALARM').length
  const warnCount   = data.filter(r => r.alarm_state === 'WARNING').length
  const divergeCount= data.filter(r => r.kalman_diverge).length

  const riskLines = [
    { key: 'risk_score_kalman',     name: 'Risk Score (Kalman)',     color: '#00d4ff', width: 2 },
    { key: 'risk_score_regression', name: 'Risk Score (Regression)', color: '#f59e0b', width: 1.5 },
  ]

  const aqiLines = [
    { key: 'AQI_kalman',     name: 'AQI Kalman',     color: '#00d4ff', width: 2 },
    { key: 'AQI_regression', name: 'AQI Regression', color: '#f59e0b', width: 1.5 },
  ]

  return (
    <div>
      <div style={{ fontSize: '0.7rem', color: '#4b5563', marginBottom: '1.25rem' }}>FAULTS & ALARM ANALYSIS</div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <MetricCard label="Fault Events"     value={faultCount}   unit="" color={faultCount > 0 ? '#ef4444' : '#10b981'} sub="total flagged samples" />
        <MetricCard label="Alarm Samples"    value={alarmCount}   unit="" color="#ef4444" sub="ALARM state count" />
        <MetricCard label="Warning Samples"  value={warnCount}    unit="" color="#f59e0b" sub="WARNING state count" />
        <MetricCard label="Kalman Divergence"value={divergeCount} unit="" color={divergeCount > 0 ? '#a855f7' : '#10b981'} sub="sanity bound violations" />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <AlarmPanel data={data} />
      </div>

      <TimeSeriesChart data={data} lines={aqiLines}  title="AQI OVER TIME — Kalman vs Regression" unit="AQI" height={220} />
      <TimeSeriesChart data={data} lines={riskLines} title="COMPOSITE RISK SCORE (threshold = 1.5)" unit="R" height={180} />

      <div className="card" style={{ marginBottom: '1rem' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e5e7eb', marginBottom: '0.75rem' }}>HYSTERESIS LOGIC</div>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.68rem', color: '#6b7280', lineHeight: 1.8 }}>
          <div>
            <span style={{ color: '#10b981' }}>NORMAL → WARNING</span> : AQI {'>'} 100 or R {'>'} 1.2<br />
            <span style={{ color: '#f59e0b' }}>WARNING → ALARM</span>  : AQI {'>'} 150 or R {'>'} 1.5
          </div>
          <div>
            <span style={{ color: '#ef4444' }}>ALARM → WARNING</span>  : AQI {'<'} 130 and R {'<'} 1.3<br />
            <span style={{ color: '#f59e0b' }}>WARNING → NORMAL</span> : AQI {'<'} 85 and R {'<'} 1.0
          </div>
        </div>
        <div style={{ fontSize: '0.62rem', color: '#4b5563', marginTop: 8 }}>
          No direct ALARM → NORMAL transition. Prevents relay chatter.
        </div>
      </div>

      <FaultLog data={data} />
    </div>
  )
}
