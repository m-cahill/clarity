/**
 * Tests for App component (M09 update).
 *
 * Tests routing and basic rendering.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../src/App";

describe("App", () => {
  it("should render the application title on home page", () => {
    render(<App />);
    expect(screen.getByText("CLARITY")).toBeInTheDocument();
  });

  it("should render the subtitle on home page", () => {
    render(<App />);
    expect(
      screen.getByText("Clinical Localization and Reasoning Integrity Testing")
    ).toBeInTheDocument();
  });

  it("should render the health indicator on home page", () => {
    render(<App />);
    expect(screen.getByTestId("health-indicator")).toBeInTheDocument();
  });

  it("should render About CLARITY section", () => {
    render(<App />);
    expect(screen.getByText("About CLARITY")).toBeInTheDocument();
  });

  it("should render footer with version", () => {
    render(<App />);
    expect(
      screen.getByText(/CLARITY v0\.0\.10.*MedGemma Impact Challenge/)
    ).toBeInTheDocument();
  });
});
