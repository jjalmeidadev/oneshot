import animate from 'tailwindcss-animate';
import type { Config } from 'tailwindcss';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        app: 'var(--bg-app)',
        surface: 'var(--bg-surface)',
        elevated: 'var(--bg-elevated)',
        muted: 'var(--bg-muted)',
        subtle: 'var(--bg-subtle)',
        border: 'var(--border)',
        'border-strong': 'var(--border-strong)',
        fg: {
          DEFAULT: 'var(--fg)',
          muted: 'var(--fg-muted)',
          subtle: 'var(--fg-subtle)',
        },
        primary: {
          DEFAULT: 'var(--primary)',
          hover: 'var(--primary-hover)',
          soft: 'var(--primary-soft)',
          fg: 'var(--primary-fg)',
        },
        success: {
          DEFAULT: 'var(--success)',
          soft: 'var(--success-soft)',
        },
        warning: {
          DEFAULT: 'var(--warning)',
          soft: 'var(--warning-soft)',
        },
        danger: {
          DEFAULT: 'var(--danger)',
          soft: 'var(--danger-soft)',
        },
        ring: 'var(--ring)',
      },
      boxShadow: {
        panel: 'var(--shadow-panel)',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'Arial', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }],
      },
    },
  },
  plugins: [animate],
} satisfies Config;
