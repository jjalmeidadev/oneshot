import { defineConfig } from '@playwright/test';
import { fileURLToPath } from 'node:url';

const python =
  process.env.E2E_PYTHON ??
  (process.platform === 'win32'
    ? fileURLToPath(new URL('../backend/.venv/Scripts/python.exe', import.meta.url))
    : 'python');

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  // HTML para leitura humana e JUnit para o relatorio de testes do MR (S5-23).
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results/e2e/junit.xml' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:5174',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
      args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'],
    },
  },
  projects: [
    {
      name: 'desktop',
      use: { browserName: 'chromium', viewport: { width: 1440, height: 900 } },
    },
    // Tablet em retrato: abaixo de 1024 px, conversas e fontes deslizam (S5-21).
    {
      name: 'tablet',
      use: { browserName: 'chromium', viewport: { width: 768, height: 1024 } },
    },
    {
      name: 'mobile',
      use: { browserName: 'chromium', viewport: { width: 390, height: 844 } },
    },
  ],
  webServer: [
    {
      command: `"${python}" -m uvicorn app.tests.e2e_server:app --host 127.0.0.1 --port 8001`,
      cwd: '../backend',
      env: { PLN_WARMUP: '0' },
      url: 'http://127.0.0.1:8001/health',
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 5174 --strictPort',
      // Timeout curto so no E2E: o cenario de timeout nao precisa esperar 120 s.
      env: { API_PROXY_TARGET: 'http://127.0.0.1:8001', VITE_API_TIMEOUT_MS: '10000' },
      url: 'http://127.0.0.1:5174',
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
