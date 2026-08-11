/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#1F3A5F',
          dark: '#162d4e',
          light: '#2a4a75',
        },
        gold: {
          DEFAULT: '#B08D2E',
          light: '#c9a84c',
          muted: '#f0e6c8',
        },
        paper: '#F4F6F9',
        status: {
          ny: '#9CA3AF',
          sett: '#06B6D4',
          interessert: '#1F3A5F',
          forkastet: '#EF4444',
          levert: '#B08D2E',
          vunnet: '#22C55E',
          tapt: '#6B7280',
        },
        resultat: {
          go: '#2ECC71',
          nogo: '#C0392B',
          forbehold: '#E67E22',
        },
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
