/**
 * Tests for HealthIndicator component.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { HealthIndicator } from "../src/HealthIndicator";
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

describe("HealthIndicator", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should show loading state initially", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<HealthIndicator />);

    expect(screen.getByText("Checking...")).toBeInTheDocument();
  });

  it("should display OK status when backend is healthy", async () => {
    vi.mocked(api.fetchHealth).mockResolvedValueOnce({
      status: "ok",
      service: "clarity-backend",
      version: "0.0.1",
    });

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByTestId("health-status")).toHaveTextContent("OK");
    });

    expect(screen.getByTestId("health-service")).toHaveTextContent(
      "clarity-backend"
    );
    expect(screen.getByTestId("health-version")).toHaveTextContent("0.0.1");
  });

  it("should display service name from backend response", async () => {
    vi.mocked(api.fetchHealth).mockResolvedValueOnce({
      status: "ok",
      service: "clarity-backend",
      version: "0.0.1",
    });

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByTestId("health-service")).toHaveTextContent(
        "clarity-backend"
      );
    });
  });

  it("should display version from backend response", async () => {
    vi.mocked(api.fetchHealth).mockResolvedValueOnce({
      status: "ok",
      service: "clarity-backend",
      version: "0.0.1",
    });

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByTestId("health-version")).toHaveTextContent("0.0.1");
    });
  });

  it("should display ERROR status when health check fails", async () => {
    vi.mocked(api.fetchHealth).mockRejectedValueOnce(
      new api.ApiError("Health check failed", 500)
    );

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByTestId("health-status")).toHaveTextContent("ERROR");
    });
  });

  it("should display error message when health check fails", async () => {
    vi.mocked(api.fetchHealth).mockRejectedValueOnce(
      new api.ApiError("Connection refused", 0)
    );

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByText("Connection refused")).toBeInTheDocument();
    });
  });

  it("should have correct test id for E2E targeting", () => {
    vi.mocked(api.fetchHealth).mockImplementation(
      () => new Promise(() => {})
    );

    render(<HealthIndicator />);

    expect(screen.getByTestId("health-indicator")).toBeInTheDocument();
  });
});
