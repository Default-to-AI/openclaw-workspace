/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'axe-bg': '#0a0e1a',
        'axe-surface': '#111827',
        'axe-border': '#1f2937',
        'axe-muted': '#374151',
        'axe-text': '#e5e7eb',
        'axe-dim': '#6b7280',
        'axe-green': '#10b981',
        'axe-yellow': '#f59e0b',
        'axe-red': '#ef4444',
        'axe-blue': '#3b82f6',
        'axe-accent': '#6366f1',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Consolas', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}

