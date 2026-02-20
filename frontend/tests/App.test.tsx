/**
 * Tests for App component.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../src/App";
import * as api from "../src/api";

// Mock the API module but keep ApiError real
vi.mock("../src/api", async (importOriginal) => {
  const actual = await importOriginal<typeof api>();
  return {
    ...actual,
    fetchHealth: vi.fn(),
    fetchVersion: vi.fn(),
  };
});

describe("App", () => {
  it("should render the application title", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {})
    );

    render(<App />);

    expect(screen.getByText("CLARITY")).toBeInTheDocument();
  });

  it("should render the subtitle", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {})
    );

    render(<App />);

    expect(
      screen.getByText("Clinical Localization and Reasoning Integrity Testing")
    ).toBeInTheDocument();
  });

  it("should render the health indicator", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {})
    );

    render(<App />);

    expect(screen.getByTestId("health-indicator")).toBeInTheDocument();
  });

  it("should render M00 information card", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {})
    );

    render(<App />);

    expect(screen.getByText("M00 — Bootstrap Complete")).toBeInTheDocument();
  });

  it("should render footer with version", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {})
    );

    render(<App />);

    expect(
      screen.getByText(/CLARITY v0\.0\.1.*MedGemma Impact Challenge/)
    ).toBeInTheDocument();
  });
});
