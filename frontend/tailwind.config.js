/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 主色调
        primary: {
          cyan: '#00E5FF',
          blue: '#0077FF',
        },
        // 背景
        background: {
          dark: '#0A0E1A',
          card: '#0F172A',
        },
        border: {
          DEFAULT: '#1E293B',
        },
        // 文字色
        text: {
          primary: '#F8FAFC',
          secondary: '#94A3B8',
          muted: '#64748B',
        },
      },
      borderRadius: {
        'sm': '6px',
        'md': '12px',
        'lg': '16px',
      },
      boxShadow: {
        'glow-cyan': '0 0 30px rgba(0, 229, 255, 0.3)',
        'glow-blue': '0 0 30px rgba(0, 119, 255, 0.3)',
        'hover-glow': '0 0 20px rgba(0, 229, 255, 0.2)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 229, 255, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 229, 255, 0.6)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      fontSize: {
        'data': ['32px', { lineHeight: '1.0', fontWeight: '700' }],
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
