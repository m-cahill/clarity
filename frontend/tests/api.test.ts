/**
 * Tests for API client functions.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fetchHealth, fetchVersion, ApiError } from "../src/api";

describe("API Client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    // Ensure clean env for each test
    vi.unstubAllEnvs();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
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
      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
      } as Response);

      await expect(fetchHealth()).rejects.toThrow(ApiError);

      // Verify status code in a separate assertion
      try {
        await fetchHealth();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).statusCode).toBe(500);
      }
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
