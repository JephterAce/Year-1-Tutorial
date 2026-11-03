const { test, expect } = require("@playwright/test");

const id = "00000000-0000-4000-8000-000000000001";

test("staging health endpoint returns application readiness", async ({ request }) => {
  const response = await request.get("/health");
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.status).toBe("ok");
});

test("student-facing pages are served in a real browser", async ({ page }) => {
  for (const [path, heading] of [
    ["/", /Think Tank|learning/i],
    ["/account", /student account/i],
    ["/assessment", /assessment|practice|test/i],
    ["/lesson?topic=" + id, /lesson|loading/i],
  ]) {
    const response = await page.goto(path);
    expect(response, path + " should return a document").not.toBeNull();
    expect(response.status(), path).toBe(200);
    await expect(page.locator("body")).toContainText(heading);
  }
});

test("account page exposes registration, sign-in and recovery controls without submitting real data", async ({ page }) => {
  await page.goto("/account");
  await expect(page.locator("#register")).toBeVisible();
  await expect(page.locator('#register input[name="email"]')).toHaveAttribute("type", "email");
  await expect(page.locator('#register input[name="password"]')).toHaveAttribute("minlength", "12");
  await expect(page.locator('#register input[name="accept_terms"]')).toBeVisible();
  await expect(page.locator('#register input[name="accept_privacy"]')).toBeVisible();
  await expect(page.locator("#login")).toBeVisible();
  await expect(page.locator("#resetRequest")).toBeVisible();
});

test("anonymous student identity and private learning APIs fail closed", async ({ request }) => {
  const checks = [
    ["GET", "/api/v1/auth/me"],
    ["GET", "/api/v1/student/profile"],
    ["GET", "/api/v1/student/assessment-history"],
    ["GET", "/api/v1/topics/" + id],
    ["GET", "/api/v1/assessment-attempts/" + id],
  ];
  for (const [method, path] of checks) {
    const response = await request.fetch(path, { method });
    expect(response.status(), method + " " + path).toBe(401);
  }
});

test("anonymous assessment and private-audio actions fail closed", async ({ request }) => {
  const attempt = await request.post("/api/v1/assessments/" + id + "/attempts", { data: {} });
  expect(attempt.status()).toBe(401);

  const audioAccess = await request.post("/api/v1/topics/" + id + "/audio/" + id + "/access", { data: {} });
  expect(audioAccess.status()).toBe(401);

  const audioStream = await request.get("/api/v1/private-audio/" + id + "/" + id);
  expect(audioStream.status()).toBe(401);
});

test("administrator identity endpoint rejects anonymous sessions", async ({ request }) => {
  const response = await request.get("/api/v1/admin/auth/me");
  expect(response.status()).toBe(401);
});

test("administrator pages redirect anonymous visitors to the dedicated login page", async ({ page }) => {
  for (const path of ["/admin", "/admin/operations", "/admin/reviews"]) {
    const response = await page.goto(path);
    expect(response.status(), path).toBe(200);
    await expect(page).toHaveURL(/\\/admin\\/login$/);
    await expect(page.getByRole("heading", { name: "Sign in securely" })).toBeVisible();
    expect(response.headers()["x-robots-tag"] || "").toContain("noindex");
  }
});

test("administrator login form is separate from student identity", async ({ page }) => {
  await page.goto("/admin/login");
  await expect(page.locator("#adminLogin")).toBeVisible();
  await expect(page.locator('input[name="email"]')).toHaveAttribute("autocomplete", "username");
  await expect(page.locator('input[name="password"]')).toHaveAttribute("autocomplete", "current-password");
});
