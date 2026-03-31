export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: { mono: ['JetBrains Mono', 'monospace'] },
      colors: {
        bg:      '#0a0e1a',
        surface: '#111827',
        border:  '#1f2937',
        accent:  '#00d4ff',
        warn:    '#f59e0b',
        danger:  '#ef4444',
        good:    '#10b981',
        muted:   '#6b7280',
      }
    }
  },
  plugins: []
}
