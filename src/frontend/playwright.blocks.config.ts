import { defineConfig } from '@playwright/test';

// Fixtures de API isolam a apresentação; integração com o backend é da #270.
export default defineConfig({
  testDir: './e2e',
  testMatch: 'response-blocks.spec.ts',
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5176',
    reducedMotion: 'reduce',
    launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH },
  },
  projects: [
    {
      name: 'desktop',
      use: { browserName: 'chromium', viewport: { width: 1440, height: 1000 } },
    },
    {
      name: 'mobile',
      use: { browserName: 'chromium', viewport: { width: 390, height: 844 } },
    },
  ],
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 5176 --strictPort',
    url: 'http://127.0.0.1:5176',
    reuseExistingServer: false,
  },
});
