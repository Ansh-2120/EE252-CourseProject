import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import StatusBar from './components/StatusBar'
import Overview from './pages/Overview'
import GasChannels from './pages/GasChannels'
import PMChannel from './pages/PMChannel'
import AlgorithmComparison from './pages/AlgorithmComparison'
import Faults from './pages/Faults'
import { loadScenario, loadMetrics } from './utils/csvLoader'

export default function App() {
  const [page,     setPage]     = useState('overview')
  const [scenario, setScenario] = useState(1)
  const [data,     setData]     = useState([])
  const [metrics,  setMetrics]  = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    setLoading(true)
    loadScenario(scenario).then(d => { setData(d); setLoading(false) })
  }, [scenario])

  useEffect(() => {
    loadMetrics().then(setMetrics)
  }, [])

  const latest = data[data.length - 1] ?? null

  const pageProps = { data, metrics }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar page={page} setPage={setPage} scenario={scenario} setScenario={setScenario} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <StatusBar latest={latest} />

        <main style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', color: '#4b5563', fontSize: '0.75rem' }}>
              Loading scenario {scenario}…
            </div>
          ) : (
            <>
              {page === 'overview'   && <Overview   {...pageProps} />}
              {page === 'gas'        && <GasChannels {...pageProps} />}
              {page === 'pm'         && <PMChannel   {...pageProps} />}
              {page === 'algorithms' && <AlgorithmComparison {...pageProps} />}
              {page === 'faults'     && <Faults      {...pageProps} />}
            </>
          )}
        </main>
      </div>
    </div>
  )
}
