/**
 * Overlay Visualization Tests (M10)
 *
 * Tests for the heatmap canvas, region overlays, and toggle controls
 * added in M10 for evidence visualization.
 */

import { describe, it, expect } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { CounterfactualConsole } from "../src/pages/CounterfactualConsole";

// Helper to render with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("M10 Overlay Visualization", () => {
  describe("Toggle Controls", () => {
    it("renders heatmap toggle control after probe run", async () => {
      renderWithRouter(<CounterfactualConsole />);

      // Wait for baselines to load
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      // Run probe
      fireEvent.click(screen.getByText("Run Probe"));

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText("Evidence Overlay")).toBeInTheDocument();
      });

      // Check toggle is present
      expect(screen.getByTestId("toggle-heatmap")).toBeInTheDocument();
    });

    it("renders regions toggle control after probe run", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("toggle-regions")).toBeInTheDocument();
      });
    });

    it("renders grid toggle control after probe run", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("toggle-grid")).toBeInTheDocument();
      });
    });

    it("renders opacity slider after probe run", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("opacity-slider")).toBeInTheDocument();
      });
    });

    it("heatmap toggle is checked by default", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        const toggle = screen.getByTestId("toggle-heatmap") as HTMLInputElement;
        expect(toggle.checked).toBe(true);
      });
    });

    it("regions toggle is checked by default", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        const toggle = screen.getByTestId("toggle-regions") as HTMLInputElement;
        expect(toggle.checked).toBe(true);
      });
    });

    it("grid toggle is unchecked by default", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        const toggle = screen.getByTestId("toggle-grid") as HTMLInputElement;
        expect(toggle.checked).toBe(false);
      });
    });

    it("can toggle heatmap off", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("toggle-heatmap")).toBeInTheDocument();
      });

      const toggle = screen.getByTestId("toggle-heatmap") as HTMLInputElement;
      fireEvent.click(toggle);
      expect(toggle.checked).toBe(false);
    });

    it("can toggle grid on", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("toggle-grid")).toBeInTheDocument();
      });

      const toggle = screen.getByTestId("toggle-grid") as HTMLInputElement;
      fireEvent.click(toggle);
      expect(toggle.checked).toBe(true);
    });

    it("can adjust opacity slider", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("opacity-slider")).toBeInTheDocument();
      });

      const slider = screen.getByTestId("opacity-slider") as HTMLInputElement;
      fireEvent.change(slider, { target: { value: "50" } });
      expect(slider.value).toBe("50");
    });
  });

  describe("Visualization Container", () => {
    it("renders overlay visualization container", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("overlay-visualization")).toBeInTheDocument();
      });
    });

    it("renders heatmap canvas when toggle is on", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("heatmap-canvas")).toBeInTheDocument();
      });
    });

    it("hides heatmap canvas when toggle is off", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("heatmap-canvas")).toBeInTheDocument();
      });

      // Turn off heatmap
      const toggle = screen.getByTestId("toggle-heatmap") as HTMLInputElement;
      fireEvent.click(toggle);

      // Canvas should be gone
      expect(screen.queryByTestId("heatmap-canvas")).not.toBeInTheDocument();
    });

    it("renders region overlay when toggle is on", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("region-overlay")).toBeInTheDocument();
      });
    });

    it("hides region overlay when toggle is off", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("region-overlay")).toBeInTheDocument();
      });

      // Turn off regions
      const toggle = screen.getByTestId("toggle-regions") as HTMLInputElement;
      fireEvent.click(toggle);

      expect(screen.queryByTestId("region-overlay")).not.toBeInTheDocument();
    });

    it("does not render grid overlay by default", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("overlay-visualization")).toBeInTheDocument();
      });

      // Grid should not be present by default
      expect(screen.queryByTestId("grid-overlay")).not.toBeInTheDocument();
    });

    it("renders grid overlay when toggle is on", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("toggle-grid")).toBeInTheDocument();
      });

      // Turn on grid
      const toggle = screen.getByTestId("toggle-grid") as HTMLInputElement;
      fireEvent.click(toggle);

      expect(screen.getByTestId("grid-overlay")).toBeInTheDocument();
    });
  });

  describe("Region Display", () => {
    it("renders region bounding boxes", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        // Mock returns 2 regions: evidence_r0 and evidence_r1
        expect(screen.getByTestId("region-evidence_r0")).toBeInTheDocument();
      });
    });

    it("renders multiple region boxes from mock", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("region-evidence_r0")).toBeInTheDocument();
        expect(screen.getByTestId("region-evidence_r1")).toBeInTheDocument();
      });
    });

    it("displays region list with count", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        // Check for "Evidence Regions (2)" header
        expect(screen.getByText(/Evidence Regions \(2\)/)).toBeInTheDocument();
      });
    });

    it("displays region IDs in list", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        // Use getAllByText since region ID appears in both overlay and list
        expect(screen.getAllByText("evidence_r0").length).toBeGreaterThanOrEqual(1);
        expect(screen.getAllByText("evidence_r1").length).toBeGreaterThanOrEqual(1);
      });
    });

    it("displays region area in list", async () => {
      renderWithRouter(<CounterfactualConsole />);

      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        // Area of 0.16 = 16.0%
        expect(screen.getByText(/Area: 16\.0%/)).toBeInTheDocument();
      });
    });
  });

  describe("Version Display", () => {
    it("displays updated version number", async () => {
      renderWithRouter(<CounterfactualConsole />);

      // Check footer shows v0.0.11
      expect(screen.getByText(/CLARITY v0\.0\.11/)).toBeInTheDocument();
    });

    it("displays M10 milestone reference", async () => {
      renderWithRouter(<CounterfactualConsole />);

      // Check subtitle shows M10
      expect(screen.getByText(/M10/)).toBeInTheDocument();
    });
  });
});

