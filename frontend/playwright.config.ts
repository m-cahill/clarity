import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E test configuration for CLARITY frontend.
 *
 * Runs against local dev servers with explicit health check wait.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html", { outputFolder: "playwright-report" }], ["list"]],
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // Web server configuration
  // In CI, we start servers manually before Playwright, so reuse them
  // Locally, Playwright can start them for us
  webServer: process.env.CI
    ? undefined
    : [
        {
          command: "cd ../backend && python -m uvicorn app.main:app --port 8000",
          url: "http://localhost:8000/health",
          reuseExistingServer: true,
          timeout: 30000,
        },
        {
          command: "npm run dev",
          url: "http://localhost:5173",
          reuseExistingServer: true,
          timeout: 30000,
          env: {
            VITE_API_URL: "http://localhost:8000",
          },
        },
      ],
});

