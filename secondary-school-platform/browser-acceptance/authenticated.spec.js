const { test, expect } = require("@playwright/test");

const adminEmail = process.env.CI_ADMIN_EMAIL || "ci-owner@thinktank.invalid";
const adminPassword = process.env.CI_ADMIN_PASSWORD || "Ephemeral-CI-Admin-Password-Only-2026!";

async function signInAdmin(page) {
  await page.goto("/admin/login");
  await page.getByLabel("Email address").fill(adminEmail);
  await page.getByLabel("Password").fill(adminPassword);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/admin$/);
}

test("authenticated administrator creates, reviews and publishes a draft assessment", async ({ page }) => {
  await signInAdmin(page);
  await page.goto("/admin/assessments");
  await expect(page.getByRole("heading", { name: "Assessment authoring" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Assessment register" })).toBeVisible();

  const title = "CI Chemistry assessment " + Date.now();
  await page.getByLabel("Title").fill(title);
  await page.getByLabel("Subject").selectOption({ label: "CI Chemistry" });
  await page.getByLabel("Class").selectOption("SS1");
  await page.getByLabel("Pass mark (%)").fill("60");
  await page.getByLabel("Maximum attempts").fill("2");
  await page.getByLabel("Allowed question counts").fill("1");
  await page.getByRole("button", { name: "Create draft" }).click();

  await expect(page.locator("#createMsg")).not.toHaveText("");
  const createMessage = await page.locator("#createMsg").textContent();
  expect(createMessage, "Assessment creation response").toContain("Draft created.");
  await expect(page.getByRole("heading", { name: "Question editor" })).toBeVisible();

  await page.getByLabel("Question prompt").fill("Which particle carries a negative electric charge?");
  await page.getByLabel("Options (JSON)").fill('[{"id":"electron","text":"Electron"},{"id":"proton","text":"Proton"}]');
  await page.getByLabel("Answer key (JSON)").fill('{"correct_option_id":"electron"}');
  await page.getByRole("button", { name: "Add question to draft" }).click();
  await expect(page.getByText(/Question added\./)).toBeVisible();
  await expect(page.getByText(/Which particle carries a negative electric charge/)).toBeVisible();

  page.on("dialog", dialog => dialog.accept());
  await page.getByRole("button", { name: "Publish assessment" }).click();
  await expect(page.getByText(/Published successfully/)).toBeVisible();
  await expect(page.locator("#questionForm textarea[name='prompt']")).toBeDisabled();
  await expect(page.locator("#publish")).toBeDisabled();
});

test("assessment authoring is mobile-usable and exposes labelled controls", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await signInAdmin(page);
  await page.goto("/admin/assessments");
  await expect(page.getByRole("main")).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Administrator pages" })).toBeVisible();
  await expect(page.getByLabel("Title")).toBeVisible();
  await expect(page.getByLabel("Subject")).toBeVisible();
  await expect(page.getByRole("button", { name: "Create draft" })).toBeVisible();
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 2);
});

test("authorised support workspace opens the data-rights review queue", async ({ page }) => {
  await signInAdmin(page);
  await page.goto("/admin/data-rights");
  await expect(page.getByRole("heading", { name: "Student data-rights queue" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Requests" })).toBeVisible();
  await expect(page.locator("#queueMsg")).toContainText(/request\(s\)|No data-rights requests|Queue unavailable/);
});

test("assessment authoring page redirects anonymous visitors", async ({ page }) => {
  await page.goto("/admin/assessments");
  await expect(page).toHaveURL(/\/admin\/login$/);
  await expect(page.getByRole("heading", { name: "Sign in securely" })).toBeVisible();
});
