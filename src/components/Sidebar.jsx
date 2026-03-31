import React from 'react'
import { Activity, Wind, Thermometer, BarChart2, AlertTriangle } from 'lucide-react'

const nav = [
  { id: 'overview',    label: 'Overview',     icon: Activity },
  { id: 'gas',         label: 'Gas Channels', icon: Wind },
  { id: 'pm',          label: 'PM Channel',   icon: Thermometer },
  { id: 'algorithms',  label: 'Algorithms',   icon: BarChart2 },
  { id: 'faults',      label: 'Faults',       icon: AlertTriangle },
]

export default function Sidebar({ page, setPage, scenario, setScenario }) {
  return (
    <aside style={{ width: 220, minHeight: '100vh', background: '#0d1117', borderRight: '1px solid #1f2937', display: 'flex', flexDirection: 'column', padding: '1.5rem 0' }}>
      <div style={{ padding: '0 1.25rem 1.5rem' }}>
        <div className="label" style={{ marginBottom: 4 }}>EE252</div>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#00d4ff', letterSpacing: '0.05em' }}>AQI MONITOR</div>
      </div>

      <div style={{ padding: '0 1rem 1.5rem', borderBottom: '1px solid #1f2937' }}>
        <div className="label" style={{ marginBottom: 8 }}>Scenario</div>
        {[1, 2, 3].map(n => (
          <button key={n} onClick={() => setScenario(n)}
            style={{ display: 'block', width: '100%', textAlign: 'left', padding: '6px 10px', marginBottom: 4, borderRadius: 6, fontSize: '0.72rem', border: 'none', cursor: 'pointer',
              background: scenario === n ? '#00d4ff22' : 'transparent',
              color: scenario === n ? '#00d4ff' : '#9ca3af',
              borderLeft: scenario === n ? '2px solid #00d4ff' : '2px solid transparent' }}>
            {n === 1 ? 'Nominal Urban' : n === 2 ? 'Pollution Spike' : 'Edge Cases'}
          </button>
        ))}
      </div>

      <nav style={{ flex: 1, padding: '1rem 1rem 0' }}>
        <div className="label" style={{ marginBottom: 8 }}>Navigation</div>
        {nav.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setPage(id)}
            style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', textAlign: 'left', padding: '8px 10px', marginBottom: 2, borderRadius: 6, fontSize: '0.72rem', border: 'none', cursor: 'pointer',
              background: page === id ? '#00d4ff15' : 'transparent',
              color: page === id ? '#00d4ff' : '#9ca3af' }}>
            <Icon size={14} />{label}
          </button>
        ))}
      </nav>
    </aside>
  )
}
