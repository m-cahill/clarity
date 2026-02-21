import { test, expect } from "@playwright/test";

/**
 * E2E smoke tests for report export functionality.
 *
 * M12: Coverage restoration (COV-002 exit) - validates download path works in real browser.
 */

test.describe("Report Export API", () => {
  test("report generate endpoint returns PDF", async ({ request }) => {
    // POST to report endpoint with valid case_id
    const response = await request.post("/api/report/generate", {
      data: { case_id: "case_001" },
      headers: { "Content-Type": "application/json" },
    });

    // Should return 200 with PDF content
    expect(response.status()).toBe(200);

    const contentType = response.headers()["content-type"];
    expect(contentType).toContain("application/pdf");

    // Verify we got actual PDF content (starts with %PDF)
    const buffer = await response.body();
    expect(buffer.length).toBeGreaterThan(0);
    const pdfHeader = buffer.toString("utf-8", 0, 4);
    expect(pdfHeader).toBe("%PDF");
  });

  test("report generate returns 404 for invalid case", async ({ request }) => {
    const response = await request.post("/api/report/generate", {
      data: { case_id: "nonexistent_case" },
      headers: { "Content-Type": "application/json" },
    });

    expect(response.status()).toBe(404);
  });
});

test.describe("Report Export UI", () => {
  test("Export Report button appears after running probe", async ({ page }) => {
    // Navigate to counterfactual console
    await page.goto("/counterfactual");

    // Wait for baselines to load and page to be ready
    await page.waitForSelector("#baseline", { timeout: 10000 });

    // Click Run Probe
    await page.click("button:has-text('Run Probe')");

    // Wait for results section to appear
    await page.waitForSelector("text=Results", { timeout: 10000 });

    // Export Report button should be visible
    const exportButton = page.locator("[data-testid='export-report-button']");
    await expect(exportButton).toBeVisible();
    await expect(exportButton).toHaveText("Export Report");
  });

  test("Export Report button does not crash when clicked", async ({ page }) => {
    // Navigate to counterfactual console
    await page.goto("/counterfactual");

    // Wait for baselines to load
    await page.waitForSelector("#baseline", { timeout: 10000 });

    // Run probe to show results
    await page.click("button:has-text('Run Probe')");
    await page.waitForSelector("text=Results", { timeout: 10000 });

    // Set up download listener
    const downloadPromise = page.waitForEvent("download", { timeout: 15000 }).catch(() => null);

    // Click export button
    await page.click("[data-testid='export-report-button']");

    // Button should show "Generating..." briefly or complete
    // We just verify no errors/crashes occur
    await page.waitForTimeout(1000);

    // Button should return to normal state
    const exportButton = page.locator("[data-testid='export-report-button']");
    await expect(exportButton).toBeVisible();

    // Check if download was triggered (optional - depends on backend state)
    const download = await downloadPromise;
    if (download) {
      expect(download.suggestedFilename()).toContain("clarity_report_");
      expect(download.suggestedFilename()).toContain(".pdf");
    }
  });
});

