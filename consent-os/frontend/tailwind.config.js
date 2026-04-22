/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'SF Pro Display', 
          'SF Pro Text',
          '-apple-system', 
          'BlinkMacSystemFont', 
          '"Segoe UI"', 
          'Roboto', 
          'Helvetica', 
          'Arial', 
          'sans-serif'
        ],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        'kanto-bg': '#f8f9fb',
        'kanto-text': '#1a1f36',
        'kanto-secondary': '#697386',
        'kanto-card': '#ffffff',
        'accent-blue': '#8a9eff',
        'accent-purple': '#b58eff',
        'accent-green': '#10b981',
        'accent-yellow': '#fbbf24',
        'risk-red': '#ef4444',
        'risk-yellow': '#f59e0b',
        'risk-green': '#10b981',
      },
      boxShadow: {
        'kanto': '0 4px 20px rgba(0, 0, 0, 0.03)',
        'kanto-hover': '0 10px 40px rgba(0, 0, 0, 0.06)',
      }
    },
  },
  plugins: [],
}
