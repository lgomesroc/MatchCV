import { defineConfig, devices } from '@playwright/test';

const liveServices = process.env.MATCHCV_LIVE_SERVICES === 'true';
const frontendBaseURL =
  process.env.MATCHCV_LIVE_FRONTEND_URL ?? 'http://127.0.0.1:4200';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'list',
  timeout: liveServices ? 900_000 : 30_000,
  expect: {
    timeout: liveServices ? 30_000 : 5_000,
  },
  use: {
    baseURL: frontendBaseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    actionTimeout: liveServices ? 30_000 : 10_000,
    navigationTimeout: liveServices ? 60_000 : 30_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  ...(liveServices
    ? {}
    : {
        webServer: {
          command: 'npm start -- --host 127.0.0.1',
          url: 'http://127.0.0.1:4200',
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          cwd: '.',
        },
      }),
});
