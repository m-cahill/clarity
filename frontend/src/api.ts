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
 * Priority:
 * 1. VITE_API_BASE_URL (canonical; set in Netlify/Render for production)
 * 2. VITE_API_URL (legacy / E2E only; can be unset if VITE_API_BASE_URL is set)
 * 3. /api (development with Vite proxy)
 */
export function getBaseUrl(): string {
  // Check for explicit API base URL (production/demo)
  const baseUrl = import.meta.env.VITE_API_BASE_URL;
  if (baseUrl) {
    return baseUrl;
  }
  // Check for legacy API URL (used in E2E tests)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl;
  }
  // Default to proxy path for dev
  return "/api";
}

/**
 * Get the current app mode.
 * Returns 'demo' if VITE_APP_MODE is set to demo, otherwise 'development'.
 */
export function getAppMode(): string {
  return import.meta.env.VITE_APP_MODE || "development";
}

/**
 * Check if the app is running in demo mode.
 */
export function isDemoMode(): boolean {
  return getAppMode() === "demo";
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

