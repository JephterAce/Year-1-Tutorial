const { defineConfig } = require("@playwright/test");

const baseURL = process.env.STAGING_BASE_URL || "https://learnwise-staging-api.onrender.com";

module.exports = defineConfig({
  testDir: ".",
  testMatch: "**/*.spec.js",
  fullyParallel: false,
  forbidOnly: true,
  retries: 0,
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
  use: {
    baseURL,
    browserName: "chromium",
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  timeout: 30_000,
});
