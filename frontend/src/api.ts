/**
 * API client for CLARITY backend communication.
 *
 * Provides type-safe fetch wrappers for backend endpoints.
 */

/** Response type for /health endpoint */
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

/** Response type for /version endpoint */
export interface VersionResponse {
  version: string;
  git_sha: string | null;
}

/** API error with status code */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Get the base URL for API calls.
 * In development with Vite proxy, use /api prefix.
 * In production or E2E, use VITE_API_URL env var.
 */
function getBaseUrl(): string {
  // Check for explicit API URL (used in E2E tests)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl;
  }
  // Default to proxy path for dev
  return "/api";
}

/**
 * Fetch health status from backend.
 *
 * @returns Promise resolving to health response
 * @throws ApiError on non-2xx response
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const baseUrl = getBaseUrl();
  const response = await fetch(`${baseUrl}/health`);

  if (!response.ok) {
    throw new ApiError(
      `Health check failed: ${response.statusText}`,
      response.status
    );
  }

  return response.json();
}

/**
 * Fetch version info from backend.
 *
 * @returns Promise resolving to version response
 * @throws ApiError on non-2xx response
 */
export async function fetchVersion(): Promise<VersionResponse> {
  const baseUrl = getBaseUrl();
  const response = await fetch(`${baseUrl}/version`);

  if (!response.ok) {
    throw new ApiError(
      `Version check failed: ${response.statusText}`,
      response.status
    );
  }

  return response.json();
}

