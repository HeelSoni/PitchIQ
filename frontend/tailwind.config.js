/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#080D1A',
        card: '#121B2D',
        border: '#1E2D4A',
        accent: {
          DEFAULT: '#00F2FE', // Neon Cyan
          hover: '#4FACFE',   // Electric Cyan Blue
        },
        success: '#00F2FE',
        warning: '#FF9F43',
        danger: '#FF4949',
        text: {
          primary: '#F8FAFC',
          secondary: '#94A3B8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
      },
      animation: {
        shimmer: 'shimmer 1.5s infinite linear',
        pulseSlow: 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      }
    },
  },
  plugins: [],
}
