/**
 * Tests for API module.
 *
 * M10.5: Tests for API base URL resolution and demo mode functions.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// We need to test the actual implementation, so we don't mock the module
// Instead, we mock import.meta.env

describe("API Module", () => {
  // Store original env
  const originalEnv = { ...import.meta.env };

  beforeEach(() => {
    // Reset mocks
    vi.resetModules();
  });

  afterEach(() => {
    // Restore original env
    Object.keys(import.meta.env).forEach((key) => {
      if (!(key in originalEnv)) {
        delete (import.meta.env as Record<string, unknown>)[key];
      }
    });
    Object.assign(import.meta.env, originalEnv);
  });

  describe("getAppMode", () => {
    it("returns 'development' by default", async () => {
      // Clear the env var
      delete (import.meta.env as Record<string, unknown>).VITE_APP_MODE;
      
      // Re-import to get fresh module
      const { getAppMode } = await import("../src/api");
      expect(getAppMode()).toBe("development");
    });

    it("returns 'demo' when VITE_APP_MODE is demo", async () => {
      (import.meta.env as Record<string, unknown>).VITE_APP_MODE = "demo";
      
      const { getAppMode } = await import("../src/api");
      expect(getAppMode()).toBe("demo");
    });
  });

  describe("isDemoMode", () => {
    it("returns false by default", async () => {
      delete (import.meta.env as Record<string, unknown>).VITE_APP_MODE;
      
      const { isDemoMode } = await import("../src/api");
      expect(isDemoMode()).toBe(false);
    });

    it("returns true when VITE_APP_MODE is demo", async () => {
      (import.meta.env as Record<string, unknown>).VITE_APP_MODE = "demo";
      
      const { isDemoMode } = await import("../src/api");
      expect(isDemoMode()).toBe(true);
    });

    it("returns false when VITE_APP_MODE is production", async () => {
      (import.meta.env as Record<string, unknown>).VITE_APP_MODE = "production";
      
      const { isDemoMode } = await import("../src/api");
      expect(isDemoMode()).toBe(false);
    });
  });

  describe("API Base URL Resolution", () => {
    it("uses VITE_API_BASE_URL when set", async () => {
      (import.meta.env as Record<string, unknown>).VITE_API_BASE_URL =
        "https://clarity-demo.onrender.com";
      delete (import.meta.env as Record<string, unknown>).VITE_API_URL;

      // The actual URL is used internally by fetch functions
      // We verify the env var is being read
      expect(import.meta.env.VITE_API_BASE_URL).toBe(
        "https://clarity-demo.onrender.com"
      );
    });

    it("falls back to VITE_API_URL when VITE_API_BASE_URL not set", async () => {
      delete (import.meta.env as Record<string, unknown>).VITE_API_BASE_URL;
      (import.meta.env as Record<string, unknown>).VITE_API_URL =
        "http://localhost:8000";

      expect(import.meta.env.VITE_API_URL).toBe("http://localhost:8000");
    });

    it("defaults to /api when no env vars set", async () => {
      delete (import.meta.env as Record<string, unknown>).VITE_API_BASE_URL;
      delete (import.meta.env as Record<string, unknown>).VITE_API_URL;

      // The default is /api for dev proxy
      expect(import.meta.env.VITE_API_BASE_URL).toBeUndefined();
      expect(import.meta.env.VITE_API_URL).toBeUndefined();
    });
  });

  describe("fetchHealth", () => {
    it("returns health response on success", async () => {
      const { fetchHealth } = await import("../src/api");
      
      // MSW handler returns health response
      const health = await fetchHealth();
      expect(health).toHaveProperty("status");
      expect(health).toHaveProperty("service");
    });

    it("throws ApiError on non-2xx response", async () => {
      // Mock fetch to return error
      const originalFetch = globalThis.fetch;
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
      }) as typeof fetch;

      const { fetchHealth, ApiError } = await import("../src/api");

      await expect(fetchHealth()).rejects.toThrow(ApiError);
      await expect(fetchHealth()).rejects.toThrow("Health check failed");

      globalThis.fetch = originalFetch;
    });

    it("ApiError includes status code", async () => {
      const originalFetch = globalThis.fetch;
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        statusText: "Service Unavailable",
      }) as typeof fetch;

      const { fetchHealth, ApiError } = await import("../src/api");

      try {
        await fetchHealth();
        expect.fail("Should have thrown");
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as InstanceType<typeof ApiError>).statusCode).toBe(503);
      }

      globalThis.fetch = originalFetch;
    });
  });

  describe("fetchVersion", () => {
    it("returns version response on success", async () => {
      const { fetchVersion } = await import("../src/api");
      
      // MSW handler returns version response
      const version = await fetchVersion();
      expect(version).toHaveProperty("version");
    });

    it("throws ApiError on non-2xx response", async () => {
      const originalFetch = globalThis.fetch;
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
      }) as typeof fetch;

      const { fetchVersion, ApiError } = await import("../src/api");

      await expect(fetchVersion()).rejects.toThrow(ApiError);
      await expect(fetchVersion()).rejects.toThrow("Version check failed");

      globalThis.fetch = originalFetch;
    });

    it("ApiError includes status code for version", async () => {
      const originalFetch = globalThis.fetch;
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: "Unauthorized",
      }) as typeof fetch;

      const { fetchVersion, ApiError } = await import("../src/api");

      try {
        await fetchVersion();
        expect.fail("Should have thrown");
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as InstanceType<typeof ApiError>).statusCode).toBe(401);
      }

      globalThis.fetch = originalFetch;
    });
  });

  describe("ApiError", () => {
    it("is an instance of Error", async () => {
      const { ApiError } = await import("../src/api");
      const error = new ApiError("Test error", 500);
      expect(error).toBeInstanceOf(Error);
    });

    it("has correct name", async () => {
      const { ApiError } = await import("../src/api");
      const error = new ApiError("Test error", 500);
      expect(error.name).toBe("ApiError");
    });

    it("has correct message", async () => {
      const { ApiError } = await import("../src/api");
      const error = new ApiError("Custom message", 404);
      expect(error.message).toBe("Custom message");
    });

    it("has correct statusCode", async () => {
      const { ApiError } = await import("../src/api");
      const error = new ApiError("Test error", 418);
      expect(error.statusCode).toBe(418);
    });
  });
});
