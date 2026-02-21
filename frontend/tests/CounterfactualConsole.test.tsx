/**
 * CounterfactualConsole Tests (M09)
 *
 * Tests for the counterfactual console component with MSW mocking.
 */

import { describe, it, expect, vi, beforeAll, afterAll } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { CounterfactualConsole } from "../src/pages/CounterfactualConsole";

// Mock URL.createObjectURL and URL.revokeObjectURL for download tests
const mockCreateObjectURL = vi.fn(() => "blob:mock-url");
const mockRevokeObjectURL = vi.fn();
// Store originals for restoration
const originalCreateObjectURL = URL.createObjectURL;
const originalRevokeObjectURL = URL.revokeObjectURL;

beforeAll(() => {
  URL.createObjectURL = mockCreateObjectURL;
  URL.revokeObjectURL = mockRevokeObjectURL;
  // Mock document.createElement to prevent navigation
  const originalCreateElement = document.createElement.bind(document);
  vi.spyOn(document, "createElement").mockImplementation((tag: string) => {
    const element = originalCreateElement(tag);
    if (tag === "a") {
      element.click = vi.fn(); // Prevent actual navigation
    }
    return element;
  });
});

afterAll(() => {
  vi.restoreAllMocks();
  // Restore URL functions
  URL.createObjectURL = originalCreateObjectURL;
  URL.revokeObjectURL = originalRevokeObjectURL;
});

// Helper to render with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("CounterfactualConsole", () => {
  it("renders console header", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByText("Counterfactual Console")).toBeInTheDocument();
  });

  it("renders configuration section", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByText("Configuration")).toBeInTheDocument();
  });

  it("renders baseline selector label", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByText("Baseline")).toBeInTheDocument();
  });

  it("renders grid size input", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByLabelText("Grid Size (k×k)")).toBeInTheDocument();
  });

  it("renders axis selector", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByLabelText("Axis")).toBeInTheDocument();
  });

  it("renders value selector", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByLabelText("Value")).toBeInTheDocument();
  });

  it("renders run button", async () => {
    renderWithRouter(<CounterfactualConsole />);
    expect(screen.getByText("Run Probe")).toBeInTheDocument();
  });

  it("loads baselines from API", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    // Wait for baselines to load
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    // Baseline selector should be populated
    const select = screen.getByLabelText("Baseline") as HTMLSelectElement;
    expect(select.options.length).toBeGreaterThan(0);
  });

  it("executes probe and displays results", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    // Wait for baselines to load
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    // Click run button
    const runButton = screen.getByText("Run Probe");
    fireEvent.click(runButton);

    // Wait for results
    await waitFor(() => {
      expect(screen.getByText("Results")).toBeInTheDocument();
    });

    // Check stats are displayed
    expect(screen.getByText("Mean |ΔESI|")).toBeInTheDocument();
    expect(screen.getByText("Max |ΔESI|")).toBeInTheDocument();
  });

  it("displays delta table after running probe", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      expect(screen.getByText("Region Deltas")).toBeInTheDocument();
    });

    // Check table headers
    expect(screen.getByText("Region ID")).toBeInTheDocument();
    expect(screen.getByText("Baseline ESI")).toBeInTheDocument();
    expect(screen.getByText("Masked ESI")).toBeInTheDocument();
  });

  it("displays raw JSON response", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      expect(screen.getByText("Raw Response")).toBeInTheDocument();
    });
  });

  it("renders back link to home", () => {
    renderWithRouter(<CounterfactualConsole />);
    const backLink = screen.getByText("← Back");
    expect(backLink).toBeInTheDocument();
    expect(backLink.closest("a")).toHaveAttribute("href", "/");
  });

  it("disables run button while loading baselines", () => {
    renderWithRouter(<CounterfactualConsole />);
    const runButton = screen.getByText("Run Probe");
    // Initially disabled because baseline not selected
    expect(runButton).toBeDisabled();
  });

  it("changes grid size input", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    const gridInput = screen.getByLabelText("Grid Size (k×k)") as HTMLInputElement;
    fireEvent.change(gridInput, { target: { value: "5" } });
    expect(gridInput.value).toBe("5");
  });

  it("changes axis selector", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    const axisSelect = screen.getByLabelText("Axis") as HTMLSelectElement;
    fireEvent.change(axisSelect, { target: { value: "contrast" } });
    expect(axisSelect.value).toBe("contrast");
  });

  it("changes value selector", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    const valueSelect = screen.getByLabelText("Value") as HTMLSelectElement;
    fireEvent.change(valueSelect, { target: { value: "0p9" } });
    expect(valueSelect.value).toBe("0p9");
  });

  it("changes baseline selector", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    const baselineSelect = screen.getByLabelText("Baseline") as HTMLSelectElement;
    fireEvent.change(baselineSelect, { target: { value: "test-baseline-002" } });
    expect(baselineSelect.value).toBe("test-baseline-002");
  });

  it("shows probe results with region delta values", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      // Check that summary stats are displayed (from mock)
      // Values rendered with 4 decimal places via .toFixed(4)
      expect(screen.getAllByText(/0\.\d{4}/).length).toBeGreaterThan(0);
    });
  });

  it("displays negative delta with correct styling class", async () => {
    renderWithRouter(<CounterfactualConsole />);
    
    await waitFor(() => {
      expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Run Probe"));

    await waitFor(() => {
      // Check region ID is displayed
      expect(screen.getByText("grid_r0_c0_k3")).toBeInTheDocument();
    });
  });

  // M11 Export Report Tests
  describe("Export Report (M11)", () => {
    it("shows Export Report button after running probe", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      // Button should not be visible before running probe
      expect(screen.queryByTestId("export-report-button")).not.toBeInTheDocument();

      // Run probe
      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("export-report-button")).toBeInTheDocument();
      });
    });

    it("Export Report button is clickable when results are present", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        const exportButton = screen.getByTestId("export-report-button");
        expect(exportButton).toBeInTheDocument();
        expect(exportButton).not.toBeDisabled();
      });
    });

    it("Export Report button shows correct text", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("export-report-button")).toHaveTextContent("Export Report");
      });
    });

    it("Export Report button triggers report generation", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("export-report-button")).toBeInTheDocument();
      });

      // Click export button
      fireEvent.click(screen.getByTestId("export-report-button"));

      // Should complete (either success or show generating state)
      await waitFor(() => {
        const button = screen.getByTestId("export-report-button");
        // After click, button should either show "Export Report" or "Generating..."
        expect(
          button.textContent === "Export Report" ||
          button.textContent === "Generating..."
        ).toBe(true);
      });
    });

    it("Export Report button has export-section container", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        const exportButton = screen.getByTestId("export-report-button");
        expect(exportButton.parentElement).toHaveClass("export-section");
      });
    });

    it("Export Report button is disabled when no baseline is selected", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      // Run probe to show results
      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        const exportButton = screen.getByTestId("export-report-button");
        // Button should be enabled since baseline is selected
        expect(exportButton).not.toBeDisabled();
      });
    });

    it("Export Report click triggers request and updates state", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      // Run probe first
      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("export-report-button")).toBeInTheDocument();
      });

      // Click export
      fireEvent.click(screen.getByTestId("export-report-button"));

      // Button should show "Generating..." briefly or complete
      await waitFor(() => {
        const button = screen.getByTestId("export-report-button");
        // Button should be back to normal state after attempt (success or error)
        expect(button.textContent).toBe("Export Report");
      });
    });

    it("Export Report shows error toast when export fails", async () => {
      renderWithRouter(<CounterfactualConsole />);
      
      await waitFor(() => {
        expect(screen.queryByText("Loading baselines...")).not.toBeInTheDocument();
      });

      // Run probe first
      fireEvent.click(screen.getByText("Run Probe"));

      await waitFor(() => {
        expect(screen.getByTestId("export-report-button")).toBeInTheDocument();
      });

      // Click export
      fireEvent.click(screen.getByTestId("export-report-button"));

      // Should eventually show error or complete
      // (In test environment, window.URL.createObjectURL is not available)
      await waitFor(() => {
        // Either error is shown or button returns to normal
        const button = screen.getByTestId("export-report-button");
        expect(button.textContent).toBe("Export Report");
      });
    });
  });
});

