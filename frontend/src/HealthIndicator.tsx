import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "./api";
import "./HealthIndicator.css";

/** State for health check */
type HealthState =
  | { status: "loading" }
  | { status: "ok"; data: HealthResponse }
  | { status: "error"; message: string };

/**
 * Health indicator component.
 *
 * Displays backend health status including service name and version.
 * Used for E2E verification that frontend can reach backend.
 */
export function HealthIndicator() {
  const [health, setHealth] = useState<HealthState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const data = await fetchHealth();
        if (!cancelled) {
          setHealth({ status: "ok", data });
        }
      } catch (error) {
        if (!cancelled) {
          const message =
            error instanceof Error ? error.message : "Unknown error";
          setHealth({ status: "error", message });
        }
      }
    }

    checkHealth();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="health-indicator" data-testid="health-indicator">
      <h2 className="health-title">Backend Status</h2>

      {health.status === "loading" && (
        <div className="health-status health-loading">
          <span className="status-dot loading" />
          <span>Checking...</span>
        </div>
      )}

      {health.status === "ok" && (
        <div className="health-status health-ok">
          <span className="status-dot ok" />
          <div className="health-details">
            <div className="health-row">
              <span className="label">Status:</span>
              <span className="value" data-testid="health-status">
                {health.data.status.toUpperCase()}
              </span>
            </div>
            <div className="health-row">
              <span className="label">Service:</span>
              <span className="value mono" data-testid="health-service">
                {health.data.service}
              </span>
            </div>
            <div className="health-row">
              <span className="label">Version:</span>
              <span className="value mono" data-testid="health-version">
                {health.data.version}
              </span>
            </div>
          </div>
        </div>
      )}

      {health.status === "error" && (
        <div className="health-status health-error">
          <span className="status-dot error" />
          <div className="health-details">
            <div className="health-row">
              <span className="label">Status:</span>
              <span className="value error" data-testid="health-status">
                ERROR
              </span>
            </div>
            <div className="health-row error-message">
              <span className="label">Message:</span>
              <span className="value">{health.message}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

