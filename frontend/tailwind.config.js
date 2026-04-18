/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        green: {
          50: '#e5fce3',
          100: '#c2f7be',
          200: '#9df095',
          300: '#76e66c',
          400: '#53db46',
          500: '#34cf28',
          600: '#149911',
          700: '#0e750c',
          800: '#095208',
          900: '#053305',
          950: '#021a02',
        },
      },
    },
  },
  plugins: [],
};