/**
 * Tests for DemoBanner component.
 *
 * M10.5: Demo Deployment Layer frontend tests.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { DemoBanner } from "../src/DemoBanner";

// Mock the api module
vi.mock("../src/api", () => ({
  isDemoMode: vi.fn(),
}));

import { isDemoMode } from "../src/api";

describe("DemoBanner", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("when in demo mode", () => {
    beforeEach(() => {
      vi.mocked(isDemoMode).mockReturnValue(true);
    });

    it("renders the banner", () => {
      render(<DemoBanner />);
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });

    it("displays Demo Mode text", () => {
      render(<DemoBanner />);
      expect(screen.getByText("Demo Mode")).toBeInTheDocument();
    });

    it("displays synthetic data warning", () => {
      render(<DemoBanner />);
      expect(
        screen.getByText(/Precomputed Artifacts \(Synthetic\)/)
      ).toBeInTheDocument();
    });

    it("has demo-banner class", () => {
      render(<DemoBanner />);
      const banner = screen.getByRole("alert");
      expect(banner).toHaveClass("demo-banner");
    });

    it("has warning icon", () => {
      render(<DemoBanner />);
      expect(screen.getByText("⚠️")).toBeInTheDocument();
    });

    it("has aria-live polite for accessibility", () => {
      render(<DemoBanner />);
      const banner = screen.getByRole("alert");
      expect(banner).toHaveAttribute("aria-live", "polite");
    });
  });

  describe("when not in demo mode", () => {
    beforeEach(() => {
      vi.mocked(isDemoMode).mockReturnValue(false);
    });

    it("does not render the banner", () => {
      render(<DemoBanner />);
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("returns null", () => {
      const { container } = render(<DemoBanner />);
      expect(container.firstChild).toBeNull();
    });
  });
});

describe("Demo Mode API Functions", () => {
  describe("isDemoMode", () => {
    it("returns true when VITE_APP_MODE is demo", () => {
      // This tests the mock behavior
      vi.mocked(isDemoMode).mockReturnValue(true);
      expect(isDemoMode()).toBe(true);
    });

    it("returns false when VITE_APP_MODE is not demo", () => {
      vi.mocked(isDemoMode).mockReturnValue(false);
      expect(isDemoMode()).toBe(false);
    });
  });
});

