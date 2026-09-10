import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json-summary'],
      include: [
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
    },
  },
});
