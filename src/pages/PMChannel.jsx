import React from 'react'
import TimeSeriesChart from '../components/TimeSeriesChart'
import MetricCard from '../components/MetricCard'

export default function PMChannel({ data }) {
  const latest = data[data.length - 1] ?? {}

  const pmLines = [
    { key: 'PM_true',       name: 'Ground Truth',  color: '#374151', width: 1, dash: '4 4' },
    { key: 'PM_corrected',  name: 'Raw Corrected', color: '#6b7280', width: 1 },
    { key: 'PM_kalman',     name: 'Kalman',        color: '#34d399', width: 2 },
    { key: 'PM_regression', name: 'Regression',    color: '#f59e0b', width: 2 },
  ]

  const aqiLines = [
    { key: 'AQI_PM_kalman',     name: 'AQI PM (Kalman)',     color: '#34d399', width: 2 },
    { key: 'AQI_PM_regression', name: 'AQI PM (Regression)', color: '#f59e0b', width: 1.5 },
  ]

  const hygroLines = [
    { key: 'RH_adc',      name: 'Humidity (%)',      color: '#60a5fa', width: 1.5 },
    { key: 'PM_corrected',name: 'PM Corrected',      color: '#34d399', width: 1.5 },
    { key: 'PM_true',     name: 'PM True',           color: '#374151', width: 1, dash: '4 4' },
  ]

  return (
    <div>
      <div style={{ fontSize: '0.7rem', color: '#4b5563', marginBottom: '1.25rem' }}>PM CHANNEL — PM2.5 / PM10</div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <MetricCard label="PM Kalman"     value={(latest.PM_kalman     ?? 0).toFixed(2)} unit="μg/m³" color="#34d399" sub={`True: ${(latest.PM_true ?? 0).toFixed(2)} μg/m³`} />
        <MetricCard label="PM Regression" value={(latest.PM_regression ?? 0).toFixed(2)} unit="μg/m³" color="#f59e0b" />
        <MetricCard label="PM Raw"        value={(latest.PM_corrected  ?? 0).toFixed(2)} unit="μg/m³" color="#6b7280" sub="env-corrected only" />
        <MetricCard label="AQI (PM)"      value={Math.round(latest.AQI_PM_kalman ?? 0)} unit=""      color="#34d399" sub="Kalman channel" />
      </div>

      <TimeSeriesChart data={data} lines={pmLines}   title="PM2.5 CONCENTRATION — Raw vs Kalman vs Regression" unit="μg/m³" height={260} />
      <TimeSeriesChart data={data} lines={aqiLines}  title="PM2.5 AQI CONTRIBUTION" unit="AQI" height={180} />

      <div className="card" style={{ marginBottom: '1rem' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e5e7eb', marginBottom: '0.75rem' }}>HYGROSCOPIC CORRECTION NOTE</div>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', lineHeight: 1.7 }}>
          Above 65% RH, particles absorb water and appear larger to the optical sensor.<br />
          Correction: <span style={{ color: '#34d399' }}>PM_true = PM_raw / f(RH)</span> where f(RH) = 1 + 0.025 × (RH − 65)<br />
          At RH = 85%: correction factor = 1.5 → 33% size overestimate without correction.
        </div>
      </div>

      <TimeSeriesChart data={data} lines={hygroLines} title="HUMIDITY vs PM — Hygroscopic Growth Effect" unit="overlay" height={180} />
    </div>
  )
}
