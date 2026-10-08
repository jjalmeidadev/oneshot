import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  test: {
    environment: 'jsdom',
    pool: 'threads',
    maxWorkers: 1,
    setupFiles: ['./src/tests/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    reporters: ['default', 'junit'],
    outputFile: { junit: 'test-results/unit/junit.xml' },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json-summary', 'cobertura'],
      include: [
        'src/App.tsx',
        'src/components/**/*.{ts,tsx}',
        'src/hooks/*.ts',
        'src/lib/**/*.ts',
        'src/state/*.tsx',
      ],
      exclude: [
        'src/lib/api/conversations.ts',
        'src/lib/api/index.ts',
        'src/lib/api/schemas.ts',
      ],
      thresholds: {
        lines: 80,
        statements: 80,
        functions: 75,
        branches: 70,
        // A média global não pode esconder um componente sem execução.
        'src/components/**/*.tsx': {
          perFile: true,
          lines: 1,
          statements: 1,
          functions: 1,
          branches: 0,
        },
      },
    },
  },
});
