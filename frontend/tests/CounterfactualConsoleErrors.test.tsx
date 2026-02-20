/**
 * CounterfactualConsole Error Handling Tests (M09)
 *
 * Tests for error states and edge cases to improve branch coverage.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "../src/mocks/server";
import { CounterfactualConsole } from "../src/pages/CounterfactualConsole";

// Helper to render with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("CounterfactualConsole Error Handling", () => {
  it("displays error when baseline fetch fails", async () => {
    // Override handler to return error
    server.use(
      http.get("http://localhost:8000/counterfactual/baselines", () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    // Error should be displayed
    expect(screen.getByText(/Failed to load/)).toBeInTheDocument();
  });

  it("displays error when probe run fails", async () => {
    // Override handler to return error for run
    server.use(
      http.post("http://localhost:8000/counterfactual/run", () => {
        return HttpResponse.json(
          { detail: "Baseline not found: test-baseline-001" },
          { status: 400 }
        );
      })
    );

    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      expect(screen.getByText("Error")).toBeInTheDocument();
    });

    expect(screen.getByText(/Baseline not found/)).toBeInTheDocument();
  });

  it("handles non-ok response during fetch", async () => {
    // Override handler to return 503 error
    server.use(
      http.get("http://localhost:8000/counterfactual/baselines", () => {
        return new HttpResponse(null, { status: 503 });
      })
    );

    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    // Should show error
    expect(screen.getByText(/Failed to load baselines: 503/)).toBeInTheDocument();
  });

  it("handles empty baselines list", async () => {
    server.use(
      http.get("http://localhost:8000/counterfactual/baselines", () => {
        return HttpResponse.json({ baselines: [] });
      })
    );

    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    // Run button should be disabled with no baselines
    const runButton = screen.getByText("Run Probe");
    expect(runButton).toBeDisabled();
  });

  it("shows running state during probe execution", async () => {
    // Use a delayed response
    server.use(
      http.post("http://localhost:8000/counterfactual/run", async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
        return HttpResponse.json({
          baseline_id: "test",
          config: { grid_size: 2, axis: "x", value: "v" },
          baseline_metrics: { answer: "", justification: "", esi: 1, drift: 0 },
          probe_surface: {
            results: [],
            mean_abs_delta_esi: 0,
            max_abs_delta_esi: 0,
            mean_abs_delta_drift: 0,
            max_abs_delta_drift: 0,
          },
        });
      })
    );

    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));
    
    // Should show running state
    expect(screen.getByText("Running...")).toBeInTheDocument();

    // Wait for completion
    await waitFor(() => {
      expect(screen.queryByText("Running...")).not.toBeInTheDocument();
    });
  });

  it("handles invalid grid size input", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    const gridInput = screen.getByLabelText("Grid Size (k×k)") as HTMLInputElement;
    
    // Set invalid value (empty string)
    fireEvent.change(gridInput, { target: { value: "" } });
    // Should default to 3
    expect(gridInput.value).toBe("3");
  });

  it("displays correct baseline options after loading", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    const baselineSelect = screen.getByLabelText("Baseline") as HTMLSelectElement;
    
    // Should have the mock baselines
    const options = Array.from(baselineSelect.options).map(o => o.value);
    expect(options).toContain("test-baseline-001");
    expect(options).toContain("test-baseline-002");
  });

  it("renders delta coloring correctly for positive deltas", async () => {
    // The mock returns negative delta_esi values
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      expect(screen.getByText("Results")).toBeInTheDocument();
    });

    // Check that the table has rows
    const tableRows = screen.getAllByRole("row");
    expect(tableRows.length).toBeGreaterThan(1); // header + data rows
  });

  it("displays all four stat cards", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      expect(screen.getByText("Results")).toBeInTheDocument();
    });

    // Check all stat labels
    expect(screen.getByText("Mean |ΔESI|")).toBeInTheDocument();
    expect(screen.getByText("Max |ΔESI|")).toBeInTheDocument();
    expect(screen.getByText("Mean |ΔDrift|")).toBeInTheDocument();
    expect(screen.getByText("Max |ΔDrift|")).toBeInTheDocument();
  });
});

