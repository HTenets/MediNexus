/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Plus Jakarta Sans', 'sans-serif'],
      },
      colors: {
        medical: {
          primary: '#0EA5E9',
          'primary-dark': '#0284C7',
          'primary-light': '#E0F2FE',
          'primary-glow': 'rgba(14, 165, 233, 0.3)',
          
          accent: '#10B981',
          'accent-dark': '#059669',
          'accent-light': '#D1FAE5',
          'accent-glow': 'rgba(16, 185, 129, 0.3)',
          
          warning: '#F59E0B',
          'warning-dark': '#D97706',
          'warning-light': '#FEF3C7',
          
          danger: '#EF4444',
          'danger-dark': '#DC2626',
          'danger-light': '#FEE2E2',
          
          purple: '#8B5CF6',
          'purple-light': '#EDE9FE',
          
          bg: '#F8FAFC',
          'bg-dark': '#0F172A',
          'bg-card': '#FFFFFF',
          
          sidebar: '#F1F5F9',
          'sidebar-dark': '#1E293B',
          
          text: {
            primary: '#1E293B',
            secondary: '#64748B',
            muted: '#94A3B8',
          },
          
          border: '#E2E8F0',
          'border-dark': 'rgba(255, 255, 255, 0.1)',
        },
      },
      boxShadow: {
        'medical-sm': '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)',
        'medical-md': '0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.05)',
        'medical-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04)',
        'medical-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        'medical-primary': '0 4px 14px rgba(14, 165, 233, 0.3)',
        'medical-accent': '0 4px 14px rgba(16, 185, 129, 0.3)',
        'glow': '0 0 20px rgba(14, 165, 233, 0.15)',
        'glow-accent': '0 0 20px rgba(16, 185, 129, 0.15)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'gradient': 'gradient 8s ease infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
