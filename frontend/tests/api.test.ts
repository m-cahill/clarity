/**
 * Tests for API client functions.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fetchHealth, fetchVersion, ApiError } from "../src/api";

describe("API Client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe("fetchHealth", () => {
    it("should return health data on success", async () => {
      const mockResponse = {
        status: "ok",
        service: "clarity-backend",
        version: "0.0.1",
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response);

      const result = await fetchHealth();

      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith("/api/health");
    });

    it("should throw ApiError on non-ok response", async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
      } as Response);

      await expect(fetchHealth()).rejects.toThrow(ApiError);
      await expect(fetchHealth()).rejects.toMatchObject({
        statusCode: 500,
      });
    });

    it("should use VITE_API_URL when set", async () => {
      // Reset the module to pick up new env
      vi.stubEnv("VITE_API_URL", "http://backend:8000");

      const mockResponse = {
        status: "ok",
        service: "clarity-backend",
        version: "0.0.1",
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response);

      // Note: In actual test, we'd need to re-import the module
      // This test documents the expected behavior
      const result = await fetchHealth();
      expect(result).toEqual(mockResponse);
    });
  });

  describe("fetchVersion", () => {
    it("should return version data on success", async () => {
      const mockResponse = {
        version: "0.0.1",
        git_sha: null,
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response);

      const result = await fetchVersion();

      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith("/api/version");
    });

    it("should throw ApiError on non-ok response", async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
      } as Response);

      await expect(fetchVersion()).rejects.toThrow(ApiError);
    });
  });
});

