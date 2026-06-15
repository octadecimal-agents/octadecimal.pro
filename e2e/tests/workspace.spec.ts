import { expect, test } from "@playwright/test";

test.describe("Octa Workspace MVP", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Agent Osobisty" })).toBeVisible();
  });

  test("boot loop: UI loads and chat greets CEO", async ({ page }) => {
    const chatLog = page.locator("#chat-log");
    await expect(chatLog).toContainText("Dzień dobry");
    await expect(chatLog).toContainText("Indeks Knowledge");
  });

  test("hash navigation opens Wiki panel", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Wiki"]').click();
    await expect(page.locator("#panel-Wiki")).toHaveClass(/active/);
    await expect(page.getByRole("heading", { name: "Knowledge — wyszukiwanie" })).toBeVisible();
  });

  test("wiki search returns Backup.md for backup Qdrant", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Wiki"]').click();
    await page.locator("#wiki-query").fill("backup Qdrant");
    await page.locator("#wiki-form").evaluate((form: HTMLFormElement) => form.requestSubmit());
    await expect(page.locator("#wiki-results")).toContainText("Backup.md");
  });

  test("dry chat answers backup question with Wiki suggestion", async ({ page }) => {
    await page.locator("#chat-input").fill("jak backup Qdrant?");
    await page.locator("#chat-form").evaluate((form: HTMLFormElement) => form.requestSubmit());
    await expect(page.locator("#chat-log")).toContainText(/Backup|Wiki|Kanon/i, { timeout: 15_000 });
    await expect(page.locator("#chat-log")).toContainText("#Wiki");
  });

  test("board CRUD: add task on #Board", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Board"]').click();
    await page.locator("#new-title").fill("E2E task Playwright");
    await page.locator("#add-task-btn").click();
    await expect(page.locator("#task-list")).toContainText("E2E task Playwright");
  });

  test("board team select lists Octa-native teams and badge reflects team", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Board"]').click();
    const teamSelect = page.locator("#new-team");
    for (const team of ["platform", "knowledge", "ops", "product"]) {
      await expect(teamSelect.locator(`option[value="${team}"]`)).toHaveText(team);
    }
    await expect(page.locator("#task-list")).toContainText("platform");
    await teamSelect.selectOption("knowledge");
    await page.locator("#new-title").fill("E2E knowledge team task");
    await page.locator("#add-task-btn").click();
    await expect(page.locator("#task-list .badge", { hasText: "knowledge" })).toBeVisible();
  });

  test("workspace health API returns expected E2E fields", async ({ request }) => {
    const res = await request.get("/workspace/health");
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.status).toMatch(/ok|degraded/);
    expect(body.knowledge_root_exists).toBe(true);
    expect(body.documents_indexed).toBeGreaterThan(0);
    expect(body.rag_backend).toBe("memory");
    expect(body.llm_provider).toBe("dry");
    expect(body.llm_active).toBe("dry");
    expect(body.calendar_provider).toBe("fixture");
    expect(body.review_pending_count).toBeGreaterThanOrEqual(3);
  });

  test("planning shows calendar source and generates plan", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Planning"]').click();
    await expect(page.locator("#calendar-list")).toContainText("Źródło kalendarza");
    await page.locator("#generate-plan-btn").click();
    await expect(page.locator("#plan-list")).not.toContainText("Brak pozycji");
  });

  test("review panel loads pending queue", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Review"]').click();
    const reviewList = page.locator("#review-list");
    await expect(reviewList).toBeVisible();
    await expect(reviewList.locator("li")).not.toHaveCount(0);
  });

  test("attention query summarizes review queue in chat", async ({ page }) => {
    await page.locator("#chat-input").fill("Co wymaga uwagi?");
    await page.locator("#chat-form").evaluate((form: HTMLFormElement) => form.requestSubmit());
    await expect(page.locator("#chat-log")).toContainText(/Review/i, { timeout: 10_000 });
    await expect(page.locator("#chat-log")).toContainText("#Review");
  });

  test("retro form saves journal entry", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Retro"]').click();
    await page.locator('input[name="went_well"]').fill("E2E retro OK");
    await page.locator('textarea[name="improve"]').fill("More automation");
    await page.locator('textarea[name="tomorrow"]').fill("Ship features");
    await page.locator("#retro-form").evaluate((form: HTMLFormElement) => form.requestSubmit());
    await expect(page.locator("#retro-preview")).toContainText("E2E retro OK");
  });

  test("review approve and reject remove items from pending queue", async ({ page }) => {
    await page.locator('.nav-link[data-hash="#Review"]').click();
    const approveButtons = page.locator("#review-list .btn-approve");
    await expect(approveButtons.first()).toBeVisible();
    const countBefore = await approveButtons.count();
    expect(countBefore).toBeGreaterThanOrEqual(2);

    const firstTitle = await page.locator("#review-list li strong").first().textContent();
    await approveButtons.first().click();
    await expect(approveButtons).toHaveCount(countBefore - 1);
    if (firstTitle) {
      await expect(page.locator("#review-list")).not.toContainText(firstTitle);
    }

    await page.locator("#review-list .btn-reject").first().click();
    await expect(approveButtons).toHaveCount(countBefore - 2);
  });
});
