import { http, HttpResponse } from "msw";

/**
 * MSW handlers for CLARITY API mocking
 *
 * M09: Counterfactual API handlers
 * M10: Added overlay_bundle mock data
 */

// Mock baselines response
const mockBaselines = {
  baselines: ["test-baseline-001", "test-baseline-002"],
};

// Generate a small mock heatmap (10x10 for testing)
const generateMockHeatmap = (width: number, height: number): number[][] => {
  const values: number[][] = [];
  for (let y = 0; y < height; y++) {
    const row: number[] = [];
    for (let x = 0; x < width; x++) {
      // Simple gradient pattern for testing
      const value = ((x + y) / (width + height - 2)) * 0.5 + 0.3;
      row.push(Math.round(value * 100000000) / 100000000);
    }
    values.push(row);
  }
  return values;
};

// Mock overlay bundle (M10)
const mockOverlayBundle = {
  evidence_map: {
    width: 10,
    height: 10,
    values: generateMockHeatmap(10, 10),
  },
  heatmap: {
    width: 10,
    height: 10,
    values: generateMockHeatmap(10, 10),
  },
  regions: [
    {
      region_id: "evidence_r0",
      x_min: 0.3,
      y_min: 0.3,
      x_max: 0.7,
      y_max: 0.7,
      area: 0.16,
    },
    {
      region_id: "evidence_r1",
      x_min: 0.1,
      y_min: 0.1,
      x_max: 0.2,
      y_max: 0.2,
      area: 0.01,
    },
  ],
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
  overlay_bundle: mockOverlayBundle,
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
      version: "0.0.11",
    });
  }),

  // POST /report/generate (M11)
  http.post("http://localhost:8000/report/generate", async ({ request }) => {
    const body = (await request.json()) as { case_id?: string };

    // Return 404 for invalid case
    if (!body.case_id || body.case_id === "invalid") {
      return HttpResponse.json(
        { detail: `Case not found: ${body.case_id || 'none'}` },
        { status: 404 }
      );
    }

    // Return a minimal valid PDF for testing
    // This is the smallest valid PDF structure
    const minimalPdf = `%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000052 00000 n 
0000000101 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
170
%%EOF`;

    return new HttpResponse(minimalPdf, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="clarity_report_${body.case_id}.pdf"`,
      },
    });
  }),
];

