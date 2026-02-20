/**
 * Home Page Tests (M09)
 *
 * Tests for the home page component.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { Home } from "../src/pages/Home";

// Helper to render with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("Home", () => {
  it("renders CLARITY title", () => {
    renderWithRouter(<Home />);
    expect(screen.getByText("CLARITY")).toBeInTheDocument();
  });

  it("renders subtitle", () => {
    renderWithRouter(<Home />);
    expect(
      screen.getByText("Clinical Localization and Reasoning Integrity Testing")
    ).toBeInTheDocument();
  });

  it("renders health indicator", () => {
    renderWithRouter(<Home />);
    // Health indicator should be present
    expect(screen.getByText(/backend/i)).toBeInTheDocument();
  });

  it("renders counterfactual nav card", () => {
    renderWithRouter(<Home />);
    expect(screen.getByText("Counterfactual Probes")).toBeInTheDocument();
  });

  it("has link to counterfactual console", () => {
    renderWithRouter(<Home />);
    const link = screen.getByText("Counterfactual Probes").closest("a");
    expect(link).toHaveAttribute("href", "/counterfactual");
  });

  it("shows disabled M10 card", () => {
    renderWithRouter(<Home />);
    expect(screen.getByText("Visualization Overlays")).toBeInTheDocument();
    expect(screen.getByText("M10 — Coming Soon")).toBeInTheDocument();
  });

  it("shows disabled M11 card", () => {
    renderWithRouter(<Home />);
    expect(screen.getByText("Report Export")).toBeInTheDocument();
    expect(screen.getByText("M11 — Coming Soon")).toBeInTheDocument();
  });

  it("renders about section", () => {
    renderWithRouter(<Home />);
    expect(screen.getByText("About CLARITY")).toBeInTheDocument();
  });

  it("renders footer with version", () => {
    renderWithRouter(<Home />);
    expect(screen.getByText(/CLARITY v0\.0\.10/)).toBeInTheDocument();
  });
});

