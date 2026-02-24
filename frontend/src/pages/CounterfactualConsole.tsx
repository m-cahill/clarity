import { useState, useEffect, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import { downloadBlob, generateReportFilename } from "../utils/downloadUtils";
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
 * Overlay region from evidence extraction
 */
interface OverlayRegion {
  region_id: string;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  area: number;
}

/**
 * Heatmap data structure
 */
interface HeatmapData {
  width: number;
  height: number;
  values: number[][];
}

/**
 * Overlay bundle from M10
 */
interface OverlayBundle {
  evidence_map: HeatmapData;
  heatmap: HeatmapData;
  regions: OverlayRegion[];
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
  overlay_bundle?: OverlayBundle;
}

/**
 * Baselines list response
 */
interface BaselinesResponse {
  baselines: string[];
}

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Fixed colormap: red scale (0 = transparent, 1 = full red)
 * Returns RGBA values
 */
function applyColormap(value: number, alpha: number): [number, number, number, number] {
  // Clamp value to [0, 1]
  const v = Math.max(0, Math.min(1, value));
  // Red scale colormap
  const r = Math.round(255 * v);
  const g = Math.round(50 * (1 - v));
  const b = Math.round(50 * (1 - v));
  const a = Math.round(255 * v * alpha);
  return [r, g, b, a];
}

/**
 * Render heatmap to canvas ImageData
 */
function renderHeatmapToImageData(
  heatmap: HeatmapData,
  alpha: number
): ImageData {
  const { width, height, values } = heatmap;
  const imageData = new ImageData(width, height);
  const data = imageData.data;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const value = values[y]?.[x] ?? 0;
      const [r, g, b, a] = applyColormap(value, alpha);
      const idx = (y * width + x) * 4;
      data[idx] = r;
      data[idx + 1] = g;
      data[idx + 2] = b;
      data[idx + 3] = a;
    }
  }

  return imageData;
}

/**
 * HeatmapCanvas — Renders heatmap overlay on canvas
 */
function HeatmapCanvas({
  heatmap,
  alpha,
  displayWidth,
  displayHeight,
}: {
  heatmap: HeatmapData;
  alpha: number;
  displayWidth: number;
  displayHeight: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas internal size to heatmap dimensions
    canvas.width = heatmap.width;
    canvas.height = heatmap.height;

    // Render heatmap
    const imageData = renderHeatmapToImageData(heatmap, alpha);
    ctx.putImageData(imageData, 0, 0);
  }, [heatmap, alpha]);

  return (
    <canvas
      ref={canvasRef}
      className="heatmap-canvas"
      style={{
        width: displayWidth,
        height: displayHeight,
      }}
      data-testid="heatmap-canvas"
    />
  );
}

/**
 * RegionOverlay — Renders bounding boxes for evidence regions
 */
function RegionOverlay({
  regions,
  displayWidth,
  displayHeight,
}: {
  regions: OverlayRegion[];
  displayWidth: number;
  displayHeight: number;
}) {
  return (
    <div
      className="region-overlay"
      style={{ width: displayWidth, height: displayHeight }}
      data-testid="region-overlay"
    >
      {regions.map((region) => {
        const left = region.x_min * displayWidth;
        const top = region.y_min * displayHeight;
        const width = (region.x_max - region.x_min) * displayWidth;
        const height = (region.y_max - region.y_min) * displayHeight;

        return (
          <div
            key={region.region_id}
            className="region-box"
            style={{
              left: `${left}px`,
              top: `${top}px`,
              width: `${width}px`,
              height: `${height}px`,
            }}
            title={`${region.region_id} (area: ${region.area.toFixed(4)})`}
            data-testid={`region-${region.region_id}`}
          >
            <span className="region-label">{region.region_id}</span>
          </div>
        );
      })}
    </div>
  );
}

/**
 * GridOverlay — Renders grid mask overlay
 */
function GridOverlay({
  gridSize,
  displayWidth,
  displayHeight,
}: {
  gridSize: number;
  displayWidth: number;
  displayHeight: number;
}) {
  const cells: { row: number; col: number }[] = [];
  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      cells.push({ row, col });
    }
  }

  const cellWidth = displayWidth / gridSize;
  const cellHeight = displayHeight / gridSize;

  return (
    <div
      className="grid-overlay"
      style={{ width: displayWidth, height: displayHeight }}
      data-testid="grid-overlay"
    >
      {cells.map(({ row, col }) => (
        <div
          key={`grid_r${row}_c${col}`}
          className="grid-cell"
          style={{
            left: `${col * cellWidth}px`,
            top: `${row * cellHeight}px`,
            width: `${cellWidth}px`,
            height: `${cellHeight}px`,
          }}
          data-testid={`grid-cell-r${row}-c${col}`}
        />
      ))}
    </div>
  );
}

/**
 * OverlayVisualization — Combined visualization component
 */
function OverlayVisualization({
  overlayBundle,
  gridSize,
  showHeatmap,
  showRegions,
  showGrid,
  heatmapOpacity,
}: {
  overlayBundle: OverlayBundle;
  gridSize: number;
  showHeatmap: boolean;
  showRegions: boolean;
  showGrid: boolean;
  heatmapOpacity: number;
}) {
  // Fixed display dimensions
  const displayWidth = 300;
  const displayHeight = 300;

  return (
    <div
      className="overlay-visualization"
      style={{ width: displayWidth, height: displayHeight }}
      data-testid="overlay-visualization"
    >
      {/* Base placeholder (gray background representing image) */}
      <div
        className="overlay-base"
        style={{ width: displayWidth, height: displayHeight }}
      />

      {/* Heatmap layer */}
      {showHeatmap && (
        <HeatmapCanvas
          heatmap={overlayBundle.heatmap}
          alpha={heatmapOpacity}
          displayWidth={displayWidth}
          displayHeight={displayHeight}
        />
      )}

      {/* Grid overlay */}
      {showGrid && (
        <GridOverlay
          gridSize={gridSize}
          displayWidth={displayWidth}
          displayHeight={displayHeight}
        />
      )}

      {/* Region overlay */}
      {showRegions && (
        <RegionOverlay
          regions={overlayBundle.regions}
          displayWidth={displayWidth}
          displayHeight={displayHeight}
        />
      )}
    </div>
  );
}

/**
 * CounterfactualConsole — Interactive probe configuration UI
 *
 * M09: Minimal console for counterfactual sweep execution
 * M10: Added visualization overlays (heatmap, regions, grid)
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

  // Overlay toggle state (M10)
  const [showHeatmap, setShowHeatmap] = useState<boolean>(true);
  const [showRegions, setShowRegions] = useState<boolean>(true);
  const [showGrid, setShowGrid] = useState<boolean>(false);
  const [heatmapOpacity, setHeatmapOpacity] = useState<number>(0.7);

  // Report export state (M11)
  const [exportingReport, setExportingReport] = useState<boolean>(false);
  const [reportError, setReportError] = useState<string | null>(null);

  // Derived: regions sorted by |ΔESI| descending (M16 — shallow copy, no mutation)
  const sortedRegions = result
    ? [...result.probe_surface.results].sort(
        (a, b) => Math.abs(b.delta_esi) - Math.abs(a.delta_esi)
      )
    : [];
  const mostImpactful = sortedRegions[0] ?? null;

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
  const runProbe = useCallback(async () => {
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
  }, [baselineId, gridSize, axis, value]);

  // Export report as PDF (M11)
  const exportReport = useCallback(async () => {
    if (!baselineId) return;

    setExportingReport(true);
    setReportError(null);

    try {
      const response = await fetch(`${API_BASE}/report/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ case_id: baselineId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Export failed: ${response.status}`);
      }

      // Get the PDF blob and trigger download using extracted helper
      const blob = await response.blob();
      const filename = generateReportFilename(baselineId);
      downloadBlob(blob, filename);
    } catch (err) {
      setReportError(err instanceof Error ? err.message : "Report export failed");
    } finally {
      setExportingReport(false);
    }
  }, [baselineId]);

  return (
    <div className="console">
      <header className="console-header">
        <Link to="/" className="back-link">
          ← Back
        </Link>
        <h1 className="console-title">Counterfactual Console</h1>
        <p className="console-subtitle">M10 — Visualization Overlays</p>
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
            <div className="results-header">
              <h2>Results</h2>
              <span className="determinism-badge">Deterministic ✓</span>
            </div>

            {/* Visualization Controls (M10) */}
            {result.overlay_bundle && (
              <div className="visualization-section">
                <h3>Evidence Overlay</h3>
                
                <div className="overlay-controls">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={showHeatmap}
                      onChange={(e) => setShowHeatmap(e.target.checked)}
                      data-testid="toggle-heatmap"
                    />
                    Show Heatmap
                  </label>
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={showRegions}
                      onChange={(e) => setShowRegions(e.target.checked)}
                      data-testid="toggle-regions"
                    />
                    Show Regions
                  </label>
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={showGrid}
                      onChange={(e) => setShowGrid(e.target.checked)}
                      data-testid="toggle-grid"
                    />
                    Show Grid
                  </label>
                  <label className="slider-label">
                    Opacity: {(heatmapOpacity * 100).toFixed(0)}%
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={heatmapOpacity * 100}
                      onChange={(e) => setHeatmapOpacity(parseInt(e.target.value) / 100)}
                      data-testid="opacity-slider"
                    />
                  </label>
                </div>

                <OverlayVisualization
                  overlayBundle={result.overlay_bundle}
                  gridSize={result.config.grid_size}
                  showHeatmap={showHeatmap}
                  showRegions={showRegions}
                  showGrid={showGrid}
                  heatmapOpacity={heatmapOpacity}
                />

                {/* Region List */}
                {result.overlay_bundle.regions.length > 0 && (
                  <div className="region-list">
                    <h4>Evidence Regions ({result.overlay_bundle.regions.length})</h4>
                    <ul>
                      {result.overlay_bundle.regions.map((region) => (
                        <li key={region.region_id}>
                          <span className="mono">{region.region_id}</span>
                          <span className="region-area">
                            Area: {(region.area * 100).toFixed(1)}%
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Export Report Button (M11) */}
            <div className="export-section">
              <button
                className="export-button"
                onClick={exportReport}
                disabled={exportingReport || !baselineId}
                data-testid="export-report-button"
              >
                {exportingReport ? "Generating..." : "Export Report"}
              </button>
              {reportError && (
                <span className="export-error" data-testid="export-error">
                  {reportError}
                </span>
              )}
            </div>

            {/* Counterfactual Summary Card (M16) */}
            {mostImpactful && (
              <div className="summary-card">
                <h3 className="summary-card-title">Counterfactual Summary</h3>
                <div className="summary-card-row">
                  <span className="summary-label">Most Impactful Region</span>
                  <span className="summary-value mono">{mostImpactful.probe.region_id}</span>
                </div>
                <div className="summary-card-row">
                  <span className="summary-label">Δ Confidence (ΔESI)</span>
                  <span
                    className={`summary-value${mostImpactful.delta_esi < 0 ? " delta-negative" : mostImpactful.delta_esi > 0 ? " delta-positive" : ""}`}
                  >
                    {mostImpactful.delta_esi.toFixed(4)}
                  </span>
                </div>
                <div className="summary-card-row">
                  <span className="summary-label">Δ Drift</span>
                  <span className="summary-value">{mostImpactful.delta_drift.toFixed(4)}</span>
                </div>
                <p className="interpretation-text">
                  {mostImpactful.delta_esi !== 0
                    ? `Masking this region changes diagnostic confidence by ${(Math.abs(mostImpactful.delta_esi) * 100).toFixed(1)}%. This indicates localized causal dependence.`
                    : "No region produced meaningful diagnostic confidence change under this probe."}
                </p>
              </div>
            )}

            {/* Summary Stats */}
            <h3>Probe Surface Statistics</h3>
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
            <div className="delta-legend" data-testid="delta-legend">
              <span className="delta-legend-item">
                <span className="delta-negative">■</span> ΔESI negative → confidence decrease under masking
              </span>
              <span className="delta-legend-item">
                <span className="delta-positive">■</span> ΔESI positive → confidence increase under masking
              </span>
              <span className="delta-legend-item">
                <span className="summary-label">ΔDrift</span> → output instability under masking
              </span>
            </div>
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
                  {sortedRegions.map((r) => (
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
          CLARITY v0.0.11 — Counterfactual Console
        </span>
      </footer>
    </div>
  );
}

export default CounterfactualConsole;
