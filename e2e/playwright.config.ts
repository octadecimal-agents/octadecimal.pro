import path from "node:path";
import { defineConfig } from "@playwright/test";

process.env.PLAYWRIGHT_BROWSERS_PATH ??= path.join(process.cwd(), ".playwright-browsers");

const baseURL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:18042";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  webServer: process.env.E2E_SKIP_SERVER
    ? undefined
    : {
        command: "bash ../scripts/octa-e2e-server.sh",
        url: `${baseURL}/workspace/health`,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
});
