/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F4F2FF',
          100: '#EAE6FF',
          200: '#D5CCFF',
          300: '#B8A8FF',
          400: '#947BFF',
          500: '#6C5CE7',
          600: '#5A46DE',
          700: '#4834C4',
          800: '#3A29A3',
          900: '#2E2082',
        },
        surface: {
          50: '#F8F9FD',
          100: '#F1F3F9',
          200: '#E4E7F2',
          card: '#FFFFFF'
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(108, 92, 231, 0.06), 0 2px 10px -2px rgba(0, 0, 0, 0.03)',
        'card': '0 10px 30px -5px rgba(28, 39, 60, 0.05)',
        'float': '0 20px 40px -10px rgba(108, 92, 231, 0.15)',
      },
      borderRadius: {
        '2xl': '20px',
        '3xl': '28px',
        '4xl': '36px',
      }
    },
  },
  plugins: [],
}
