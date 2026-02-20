import { test, expect } from "@playwright/test";

/**
 * E2E tests for health endpoint verification.
 *
 * These tests verify that the frontend can successfully
 * communicate with the backend and display real response values.
 */

test.describe("Health E2E Verification", () => {
  test("should display backend health status on page load", async ({
    page,
  }) => {
    await page.goto("/");

    // Wait for the health indicator to be present
    const healthIndicator = page.getByTestId("health-indicator");
    await expect(healthIndicator).toBeVisible();

    // Wait for loading to complete and status to appear
    const statusElement = page.getByTestId("health-status");
    await expect(statusElement).toBeVisible({ timeout: 10000 });
    await expect(statusElement).toHaveText("OK");
  });

  test("should display service name from backend response", async ({
    page,
  }) => {
    await page.goto("/");

    // Verify service name matches backend response
    const serviceElement = page.getByTestId("health-service");
    await expect(serviceElement).toBeVisible({ timeout: 10000 });
    await expect(serviceElement).toHaveText("clarity-backend");
  });

  test("should display version from backend response", async ({ page }) => {
    await page.goto("/");

    // Verify version matches backend response
    const versionElement = page.getByTestId("health-version");
    await expect(versionElement).toBeVisible({ timeout: 10000 });
    await expect(versionElement).toHaveText("0.0.1");
  });

  test("should render CLARITY title", async ({ page }) => {
    await page.goto("/");

    // Use exact matching to avoid "About CLARITY" heading
    const title = page.getByRole("heading", { name: "CLARITY", exact: true });
    await expect(title).toBeVisible();
  });

  test("should render complete health status with all fields", async ({
    page,
  }) => {
    await page.goto("/");

    // Wait for health check to complete
    const statusElement = page.getByTestId("health-status");
    await expect(statusElement).toHaveText("OK", { timeout: 10000 });

    // Verify all required fields are present
    await expect(page.getByTestId("health-service")).toHaveText(
      "clarity-backend"
    );
    await expect(page.getByTestId("health-version")).toHaveText("0.0.1");

    // This test proves the frontend successfully reaches the backend
    // and displays real values from the /health endpoint response
  });
});

