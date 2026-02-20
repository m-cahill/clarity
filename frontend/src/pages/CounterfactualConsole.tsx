import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./CounterfactualConsole.css";

/**
 * Request body for counterfactual run
 */
interface CounterfactualRunRequest {
  baseline_id: string;
  grid_size: number;
  axis: string;
  value: string;
}

/**
 * Probe result from a single region
 */
interface ProbeResultItem {
  probe: {
    region_id: string;
    axis: string;
    value: string;
  };
  baseline_esi: number;
  masked_esi: number;
  delta_esi: number;
  baseline_drift: number;
  masked_drift: number;
  delta_drift: number;
}

/**
 * Full response from counterfactual run endpoint
 */
interface CounterfactualRunResponse {
  baseline_id: string;
  config: {
    grid_size: number;
    axis: string;
    value: string;
  };
  baseline_metrics: {
    answer: string;
    justification: string;
    esi: number;
    drift: number;
  };
  probe_surface: {
    results: ProbeResultItem[];
    mean_abs_delta_esi: number;
    max_abs_delta_esi: number;
    mean_abs_delta_drift: number;
    max_abs_delta_drift: number;
  };
}

/**
 * Baselines list response
 */
interface BaselinesResponse {
  baselines: string[];
}

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * CounterfactualConsole — Interactive probe configuration UI
 *
 * M09: Minimal console for counterfactual sweep execution
 */
export function CounterfactualConsole() {
  // Form state
  const [baselineId, setBaselineId] = useState<string>("");
  const [gridSize, setGridSize] = useState<number>(3);
  const [axis, setAxis] = useState<string>("brightness");
  const [value, setValue] = useState<string>("1p0");

  // Available baselines
  const [baselines, setBaselines] = useState<string[]>([]);
  const [baselinesLoading, setBaselinesLoading] = useState<boolean>(true);
  const [baselinesError, setBaselinesError] = useState<string | null>(null);

  // Run state
  const [running, setRunning] = useState<boolean>(false);
  const [result, setResult] = useState<CounterfactualRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load available baselines on mount
  useEffect(() => {
    const loadBaselines = async () => {
      try {
        const response = await fetch(`${API_BASE}/counterfactual/baselines`);
        if (!response.ok) {
          throw new Error(`Failed to load baselines: ${response.status}`);
        }
        const data: BaselinesResponse = await response.json();
        setBaselines(data.baselines);
        if (data.baselines.length > 0) {
          setBaselineId(data.baselines[0]);
        }
        setBaselinesError(null);
      } catch (err) {
        setBaselinesError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setBaselinesLoading(false);
      }
    };

    loadBaselines();
  }, []);

  // Run counterfactual probe
  const runProbe = async () => {
    setRunning(true);
    setError(null);
    setResult(null);

    try {
      const request: CounterfactualRunRequest = {
        baseline_id: baselineId,
        grid_size: gridSize,
        axis: axis,
        value: value,
      };

      const response = await fetch(`${API_BASE}/counterfactual/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      const data: CounterfactualRunResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="console">
      <header className="console-header">
        <Link to="/" className="back-link">
          ← Back
        </Link>
        <h1 className="console-title">Counterfactual Console</h1>
        <p className="console-subtitle">M09 — Interactive Probe Execution</p>
      </header>

      <main className="console-main">
        {/* Configuration Form */}
        <section className="config-section">
          <h2>Configuration</h2>

          <div className="form-group">
            <label htmlFor="baseline">Baseline</label>
            {baselinesLoading ? (
              <span className="loading-text">Loading baselines...</span>
            ) : baselinesError ? (
              <span className="error-text">{baselinesError}</span>
            ) : (
              <select
                id="baseline"
                value={baselineId}
                onChange={(e) => setBaselineId(e.target.value)}
                disabled={running}
              >
                {baselines.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="gridSize">Grid Size (k×k)</label>
            <input
              id="gridSize"
              type="number"
              min={1}
              max={10}
              value={gridSize}
              onChange={(e) => setGridSize(parseInt(e.target.value) || 3)}
              disabled={running}
            />
          </div>

          <div className="form-group">
            <label htmlFor="axis">Axis</label>
            <select
              id="axis"
              value={axis}
              onChange={(e) => setAxis(e.target.value)}
              disabled={running}
            >
              <option value="brightness">brightness</option>
              <option value="contrast">contrast</option>
              <option value="blur">blur</option>
              <option value="noise">noise</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="value">Value</label>
            <select
              id="value"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              disabled={running}
            >
              <option value="0p8">0p8</option>
              <option value="0p9">0p9</option>
              <option value="1p0">1p0</option>
              <option value="1p1">1p1</option>
              <option value="1p2">1p2</option>
            </select>
          </div>

          <button
            className="run-button"
            onClick={runProbe}
            disabled={running || !baselineId}
          >
            {running ? "Running..." : "Run Probe"}
          </button>
        </section>

        {/* Error Display */}
        {error && (
          <section className="error-section">
            <h2>Error</h2>
            <p className="error-message">{error}</p>
          </section>
        )}

        {/* Results Display */}
        {result && (
          <section className="results-section">
            <h2>Results</h2>

            {/* Summary Stats */}
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Mean |ΔESI|</span>
                <span className="stat-value">
                  {result.probe_surface.mean_abs_delta_esi.toFixed(4)}
                </span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Max |ΔESI|</span>
                <span className="stat-value">
                  {result.probe_surface.max_abs_delta_esi.toFixed(4)}
                </span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Mean |ΔDrift|</span>
                <span className="stat-value">
                  {result.probe_surface.mean_abs_delta_drift.toFixed(4)}
                </span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Max |ΔDrift|</span>
                <span className="stat-value">
                  {result.probe_surface.max_abs_delta_drift.toFixed(4)}
                </span>
              </div>
            </div>

            {/* Delta Table */}
            <h3>Region Deltas</h3>
            <div className="delta-table-container">
              <table className="delta-table">
                <thead>
                  <tr>
                    <th>Region ID</th>
                    <th>Baseline ESI</th>
                    <th>Masked ESI</th>
                    <th>ΔESI</th>
                    <th>ΔDrift</th>
                  </tr>
                </thead>
                <tbody>
                  {result.probe_surface.results.map((r) => (
                    <tr key={r.probe.region_id}>
                      <td className="mono">{r.probe.region_id}</td>
                      <td>{r.baseline_esi.toFixed(4)}</td>
                      <td>{r.masked_esi.toFixed(4)}</td>
                      <td
                        className={
                          r.delta_esi < 0
                            ? "delta-negative"
                            : r.delta_esi > 0
                            ? "delta-positive"
                            : ""
                        }
                      >
                        {r.delta_esi.toFixed(4)}
                      </td>
                      <td
                        className={
                          r.delta_drift > 0
                            ? "delta-positive"
                            : r.delta_drift < 0
                            ? "delta-negative"
                            : ""
                        }
                      >
                        {r.delta_drift.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Raw JSON */}
            <h3>Raw Response</h3>
            <pre className="json-output">
              {JSON.stringify(result, null, 2)}
            </pre>
          </section>
        )}
      </main>

      <footer className="console-footer">
        <span className="mono text-secondary">
          CLARITY v0.0.10 — Counterfactual Console
        </span>
      </footer>
    </div>
  );
}

export default CounterfactualConsole;

