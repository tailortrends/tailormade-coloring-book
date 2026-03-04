/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#2b6cee',
        'primary-dark': '#1a4bb0',
        'primary-light': '#eef4ff',
        'primary-hover': '#1a5ac6',
        'accent-purple': '#8b5cf6',
        'accent-pink': '#ec4899',
        'accent-orange': '#f97316',
        'background-light': '#f6f6f8',
        'background-dark': '#101622',
        'surface-light': '#ffffff',
        'surface-dark': '#1e293b',
        'text-main': '#0f172a',
        'text-sub': '#475569',
        'text-secondary': '#616f89',
      },
      fontFamily: {
        display: ['Plus Jakarta Sans', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '1rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '3rem',
        full: '9999px',
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        shimmer: 'shimmer 2s infinite',
      },
      keyframes: {
        float: {
          '0%': { transform: 'translateY(0px) rotate(0deg)' },
          '50%': { transform: 'translateY(-20px) rotate(5deg)' },
          '100%': { transform: 'translateY(0px) rotate(0deg)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
