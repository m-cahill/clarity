/**
 * CounterfactualConsole Tests (M09)
 *
 * Tests for the counterfactual console component with MSW mocking.
 */

import { describe, it, expect } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { CounterfactualConsole } from "../src/pages/CounterfactualConsole";

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
});

