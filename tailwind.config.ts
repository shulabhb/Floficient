import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        emerald: {
          300: '#6ee7b7',
          400: '#34d399',
        },
        blue: {
          400: '#60a5fa',
          500: '#3b82f6',
        },
        gray: {
          950: '#0f172a',
          900: '#1e293b',
          800: '#334155',
          700: '#475569',
          400: '#94a3b8',
          300: '#cbd5e1',
        },
      },
    },
  },
  safelist: [
    'bg-emerald-400',
    'bg-blue-400',
    'text-emerald-400',
    'text-blue-400',
  ],
  plugins: [],
};
export default config; 