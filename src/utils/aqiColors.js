export function aqiColor(val) {
  if (val <= 50)  return '#10b981'
  if (val <= 100) return '#facc15'
  if (val <= 150) return '#f97316'
  if (val <= 200) return '#ef4444'
  if (val <= 300) return '#a855f7'
  return '#7f1d1d'
}

export function aqiLabel(val) {
  if (val <= 50)  return 'Good'
  if (val <= 100) return 'Moderate'
  if (val <= 150) return 'Unhealthy (Sensitive)'
  if (val <= 200) return 'Unhealthy'
  if (val <= 300) return 'Very Unhealthy'
  return 'Hazardous'
}

export function alarmColor(state) {
  if (state === 'NORMAL')  return '#10b981'
  if (state === 'WARNING') return '#f59e0b'
  if (state === 'ALARM')   return '#ef4444'
  return '#6b7280'
}
