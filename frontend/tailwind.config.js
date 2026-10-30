/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Atkinson Hyperlegible"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        surface: '#F5F6F7',
        ink: '#1A1F24',
        secondary: '#6B7680',
        hairline: '#E3E7EA',
        accent: '#E4572E',
        backbone: '#B8C0C6',
        dna: {
          A: '#2F9E5F',
          T: '#D64545',
          G: '#E3B023',
          C: '#2F6FDE',
          N: '#6B7680',
        },
      },
    },
  },
  plugins: [],
};
