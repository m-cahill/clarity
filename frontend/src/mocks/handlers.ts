import { http, HttpResponse } from "msw";

/**
 * MSW handlers for CLARITY API mocking
 *
 * M09: Counterfactual API handlers
 */

// Mock baselines response
const mockBaselines = {
  baselines: ["test-baseline-001", "test-baseline-002"],
};

// Mock counterfactual run response
const mockProbeResult = {
  baseline_id: "test-baseline-001",
  config: {
    grid_size: 3,
    axis: "brightness",
    value: "1p0",
  },
  baseline_metrics: {
    answer: "Normal findings.",
    justification: "No abnormalities detected.",
    esi: 1.0,
    drift: 0.0,
  },
  probe_surface: {
    results: [
      {
        probe: { region_id: "grid_r0_c0_k3", axis: "brightness", value: "1p0" },
        baseline_esi: 1.0,
        masked_esi: 0.9,
        delta_esi: -0.1,
        baseline_drift: 0.0,
        masked_drift: 0.1,
        delta_drift: 0.1,
      },
      {
        probe: { region_id: "grid_r0_c1_k3", axis: "brightness", value: "1p0" },
        baseline_esi: 1.0,
        masked_esi: 0.8,
        delta_esi: -0.2,
        baseline_drift: 0.0,
        masked_drift: 0.2,
        delta_drift: 0.2,
      },
      {
        probe: { region_id: "grid_r0_c2_k3", axis: "brightness", value: "1p0" },
        baseline_esi: 1.0,
        masked_esi: 0.7,
        delta_esi: -0.3,
        baseline_drift: 0.0,
        masked_drift: 0.3,
        delta_drift: 0.3,
      },
      {
        probe: { region_id: "grid_r1_c0_k3", axis: "brightness", value: "1p0" },
        baseline_esi: 1.0,
        masked_esi: 0.6,
        delta_esi: -0.4,
        baseline_drift: 0.0,
        masked_drift: 0.4,
        delta_drift: 0.4,
      },
    ],
    mean_abs_delta_esi: 0.25,
    max_abs_delta_esi: 0.4,
    mean_abs_delta_drift: 0.25,
    max_abs_delta_drift: 0.4,
  },
};

export const handlers = [
  // GET /counterfactual/baselines
  http.get("http://localhost:8000/counterfactual/baselines", () => {
    return HttpResponse.json(mockBaselines);
  }),

  // POST /counterfactual/run
  http.post("http://localhost:8000/counterfactual/run", async ({ request }) => {
    const body = (await request.json()) as { baseline_id?: string };

    // Return error for invalid baseline
    if (body.baseline_id === "invalid") {
      return HttpResponse.json(
        { detail: "Baseline not found: invalid" },
        { status: 400 }
      );
    }

    return HttpResponse.json(mockProbeResult);
  }),

  // Health endpoint - full URL
  http.get("http://localhost:8000/health", () => {
    return HttpResponse.json({
      status: "healthy",
      service: "clarity-backend",
      version: "0.0.10",
    });
  }),

  // Health endpoint - relative URL for API proxy
  http.get("/api/health", () => {
    return HttpResponse.json({
      status: "healthy",
      service: "clarity-backend",
      version: "0.0.10",
    });
  }),
];

