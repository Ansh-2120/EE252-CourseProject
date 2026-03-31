import React from 'react'
import TimeSeriesChart from '../components/TimeSeriesChart'
import ComparisonTable from '../components/ComparisonTable'

export default function AlgorithmComparison({ data, metrics }) {
  const rmseLines = [
    { key: 'RMSE_CO_kalman',     name: 'RMSE CO Kalman',     color: '#00d4ff', width: 2 },
    { key: 'RMSE_CO_regression', name: 'RMSE CO Regression', color: '#f59e0b', width: 2 },
  ]

  const coCompLines = [
    { key: 'C_CO_true',       name: 'Ground Truth', color: '#374151', width: 1, dash: '4 4' },
    { key: 'C_CO_kalman',     name: 'Kalman',       color: '#00d4ff', width: 2 },
    { key: 'C_CO_regression', name: 'Regression',   color: '#f59e0b', width: 2 },
  ]

  const no2CompLines = [
    { key: 'C_NO2_true',       name: 'Ground Truth', color: '#374151', width: 1, dash: '4 4' },
    { key: 'C_NO2_kalman',     name: 'Kalman',       color: '#818cf8', width: 2 },
    { key: 'C_NO2_regression', name: 'Regression',   color: '#f59e0b', width: 2 },
  ]

  const pmCompLines = [
    { key: 'PM_true',       name: 'Ground Truth', color: '#374151', width: 1, dash: '4 4' },
    { key: 'PM_kalman',     name: 'Kalman',       color: '#34d399', width: 2 },
    { key: 'PM_regression', name: 'Regression',   color: '#f59e0b', width: 2 },
  ]

  return (
    <div>
      <div style={{ fontSize: '0.7rem', color: '#4b5563', marginBottom: '1.25rem' }}>ALGORITHM COMPARISON — KALMAN vs REGRESSION</div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <div className="card" style={{ flex: 1 }}>
          <div className="label" style={{ marginBottom: 8 }}>Algorithm A</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#00d4ff' }}>Extended Kalman Filter</div>
          <div style={{ fontSize: '0.65rem', color: '#6b7280', marginTop: 6, lineHeight: 1.6 }}>
            State-space model. Predict + Update cycle per sample.<br />
            Optimal under Gaussian noise. Handles dynamic drift.
          </div>
        </div>
        <div className="card" style={{ flex: 1 }}>
          <div className="label" style={{ marginBottom: 8 }}>Algorithm B</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f59e0b' }}>Polynomial Regression</div>
          <div style={{ fontSize: '0.65rem', color: '#6b7280', marginTop: 6, lineHeight: 1.6 }}>
            8-feature model + rolling baseline tracker.<br />
            Trained on Scenario 1. Lower compute cost.
          </div>
        </div>
      </div>

      <ComparisonTable metrics={metrics} />

      <div style={{ marginTop: '1rem' }}>
        <TimeSeriesChart data={data} lines={coCompLines}  title="CO — Kalman vs Regression vs Truth"  unit="ppm"    height={200} />
        <TimeSeriesChart data={data} lines={no2CompLines} title="NO₂ — Kalman vs Regression vs Truth" unit="ppb"    height={200} />
        <TimeSeriesChart data={data} lines={pmCompLines}  title="PM — Kalman vs Regression vs Truth"  unit="μg/m³"  height={200} />
        <TimeSeriesChart data={data} lines={rmseLines}    title="ROLLING RMSE — CO Channel (60-sample window)" unit="ppm" height={180} />
      </div>
    </div>
  )
}
