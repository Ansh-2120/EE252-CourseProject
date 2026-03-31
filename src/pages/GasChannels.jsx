import React from 'react'
import TimeSeriesChart from '../components/TimeSeriesChart'
import MetricCard from '../components/MetricCard'

export default function GasChannels({ data }) {
  const latest = data[data.length - 1] ?? {}

  const coLines = [
    { key: 'C_CO_true',       name: 'Ground Truth', color: '#374151', width: 1, dash: '4 4' },
    { key: 'C_CO_corrected',  name: 'Raw Corrected', color: '#6b7280', width: 1 },
    { key: 'C_CO_kalman',     name: 'Kalman',        color: '#00d4ff', width: 2 },
    { key: 'C_CO_regression', name: 'Regression',    color: '#f59e0b', width: 2 },
  ]

  const no2Lines = [
    { key: 'C_NO2_true',       name: 'Ground Truth',  color: '#374151', width: 1, dash: '4 4' },
    { key: 'C_NO2_corrected',  name: 'Raw Corrected', color: '#6b7280', width: 1 },
    { key: 'C_NO2_kalman',     name: 'Kalman',        color: '#818cf8', width: 2 },
    { key: 'C_NO2_regression', name: 'Regression',    color: '#f59e0b', width: 2 },
  ]

  const envLines = [
    { key: 'T_adc',  name: 'Temperature (°C)', color: '#fb923c', width: 1.5 },
    { key: 'RH_adc', name: 'Humidity (%)',      color: '#60a5fa', width: 1.5 },
  ]

  return (
    <div>
      <div style={{ fontSize: '0.7rem', color: '#4b5563', marginBottom: '1.25rem' }}>GAS CHANNELS — CO + NO₂</div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <MetricCard label="CO Kalman"     value={(latest.C_CO_kalman     ?? 0).toFixed(3)} unit="ppm" color="#00d4ff" sub={`True: ${(latest.C_CO_true ?? 0).toFixed(3)} ppm`} />
        <MetricCard label="CO Regression" value={(latest.C_CO_regression ?? 0).toFixed(3)} unit="ppm" color="#f59e0b" />
        <MetricCard label="NO₂ Kalman"    value={(latest.C_NO2_kalman    ?? 0).toFixed(1)} unit="ppb" color="#818cf8" sub={`True: ${(latest.C_NO2_true ?? 0).toFixed(1)} ppb`} />
        <MetricCard label="NO₂ Regression"value={(latest.C_NO2_regression?? 0).toFixed(1)} unit="ppb" color="#f59e0b" />
      </div>

      <TimeSeriesChart data={data} lines={coLines}  title="CO CONCENTRATION — Raw vs Kalman vs Regression" unit="ppm" height={240} />
      <TimeSeriesChart data={data} lines={no2Lines} title="NO₂ CONCENTRATION — Raw vs Kalman vs Regression" unit="ppb" height={240} />
      <TimeSeriesChart data={data} lines={envLines} title="ENVIRONMENTAL CONDITIONS — Temperature & Humidity" unit="°C / %" height={180} />
    </div>
  )
}
