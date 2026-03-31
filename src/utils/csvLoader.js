import Papa from 'papaparse'

export async function loadCSV(path) {
  const res  = await fetch(path)
  const text = await res.text()
  const { data } = Papa.parse(text, { header: true, dynamicTyping: true, skipEmptyLines: true })
  return data
}

export async function loadScenario(n) {
  return loadCSV(`/data/scenario${n}_output.csv`)
}

export async function loadMetrics() {
  return loadCSV('/data/comparison_metrics.csv')
}
