/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,svelte}'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecf5ff',
          100: '#d9ecff',
          200: '#b3d8ff',
          300: '#8cc5ff',
          400: '#66b1ff',
          500: '#409eff',
          600: '#337ecc',
          700: '#265f99',
          800: '#1a3f66',
          900: '#0d2033'
        },
        success: {
          50: '#f0f9ff',
          100: '#e1f3ff',
          200: '#c2e7ff',
          300: '#a3dbff',
          400: '#84cfff',
          500: '#67c23a',
          600: '#529b2e',
          700: '#3e7423',
          800: '#294e17',
          900: '#15270c'
        },
        warning: {
          50: '#fdf6ec',
          100: '#fbedd9',
          200: '#f7dbb3',
          300: '#f3c98d',
          400: '#efb767',
          500: '#e6a23c',
          600: '#b88230',
          700: '#8a6124',
          800: '#5c4118',
          900: '#2e200c'
        },
        danger: {
          50: '#fef0f0',
          100: '#fde1e1',
          200: '#fbc3c3',
          300: '#f9a5a5',
          400: '#f78787',
          500: '#f56c6c',
          600: '#c45656',
          700: '#934141',
          800: '#622b2b',
          900: '#311616'
        }
      }
    }
  },
  plugins: []
}

