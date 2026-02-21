import { test, expect } from "@playwright/test";

/**
 * E2E smoke tests for demo deployment layer.
 *
 * M10.5: These tests verify demo artifacts are served correctly.
 */

test.describe("Demo API Smoke Tests", () => {
  test("demo health endpoint returns 200", async ({ request }) => {
    const response = await request.get("/api/demo/health");
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.status).toBe("ok");
    expect(data).toHaveProperty("mode");
    expect(data).toHaveProperty("artifact_root");
  });

  test("demo cases list returns case_001", async ({ request }) => {
    const response = await request.get("/api/demo/cases");
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty("cases");
    expect(data).toHaveProperty("total");

    const caseIds = data.cases.map((c: { case_id: string }) => c.case_id);
    expect(caseIds).toContain("case_001");
  });

  test("demo surface artifact loads for case_001", async ({ request }) => {
    const response = await request.get("/api/demo/cases/case_001/surface");
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.artifact_type).toBe("robustness_surface");
    expect(data.case_id).toBe("case_001");
    expect(data).toHaveProperty("data");
  });
});

test.describe("Demo Artifact Integrity", () => {
  test("demo artifacts pass integrity verification", async ({ request }) => {
    const response = await request.get("/api/demo/cases/case_001/verify");
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.case_id).toBe("case_001");
    expect(data.valid).toBe(true);
  });
});

