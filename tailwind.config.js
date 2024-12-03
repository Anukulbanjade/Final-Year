module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette
        primary: {
          50: '#e6f2ff',
          100: '#b3d9ff',
          900: '#64379f'
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--gradient-color-stops))',
      },
      animation: {
        'progressFill': 'progressFill 2s ease-in-out infinite'
      },
      keyframes: {
        progressFill: {
          '0%, 100%': { width: '0%' },
          '50%': { width: '100%' }
        }
      }
    }
  },
  plugins: [],
}