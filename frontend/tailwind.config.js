//
// REPLACE THIS FILE
// File: peptalk/frontend/tailwind.config.js
//
/** @type {import('tailwindcss').Config} */
const { colors: defaultColors } = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // --- Custom Color Palette (RGB for opacity support) ---
        'primary-mint': 'rgb(22 110 63)',       // Mintlify's Primary Green
        'primary-light-mint': 'rgb(38 189 108)', // Mintlify's Light Green Accent
        'background-light-mint': 'rgb(255 255 255)', // White
        'background-dark-mint': 'rgb(10 13 13)',     // Near Black (for dark mode support)
        'gray-mint': {
          50: 'rgb(243 246 244)',
          100: 'rgb(238 241 239)',
          200: 'rgb(223 225 224)', // Used for borders
          400: 'rgb(159 161 160)',
          700: 'rgb(63 65 64)',
          900: 'rgb(23 26 24)',
        }
      },
      fontFamily: {
        // Adding Geist Mono for code blocks (as observed in the HTML)
        'mono-geist': ['Geist Mono', 'Menlo', 'Monaco', 'monospace'],
      },
      spacing: {
        // Custom width for the sidebar (16.5rem = 264px, matching Mintlify)
        '16.5': '16.5rem', 
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}