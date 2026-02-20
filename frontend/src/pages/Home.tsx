import { Link } from "react-router-dom";
import { HealthIndicator } from "../HealthIndicator";
import "./Home.css";

/**
 * Home — Landing page with health indicator and navigation
 *
 * M00 skeleton with M09 navigation added
 */
export function Home() {
  return (
    <div className="home">
      <header className="home-header">
        <h1 className="home-title">CLARITY</h1>
        <p className="home-subtitle">
          Clinical Localization and Reasoning Integrity Testing
        </p>
      </header>

      <main className="home-main">
        <section className="status-section">
          <HealthIndicator />
        </section>

        <section className="nav-section">
          <h2>Evaluation Console</h2>
          <div className="nav-cards">
            <Link to="/counterfactual" className="nav-card">
              <h3>Counterfactual Probes</h3>
              <p>
                Execute region-masking probes to measure causal evidence
                dependence.
              </p>
              <span className="nav-card-tag">M09</span>
            </Link>

            <div className="nav-card nav-card-disabled">
              <h3>Visualization Overlays</h3>
              <p>Evidence map overlays and saliency heatmaps.</p>
              <span className="nav-card-tag">M10 — Coming Soon</span>
            </div>

            <div className="nav-card nav-card-disabled">
              <h3>Report Export</h3>
              <p>Deterministic PDF report generation.</p>
              <span className="nav-card-tag">M11 — Coming Soon</span>
            </div>
          </div>
        </section>

        <section className="info-section">
          <div className="info-card">
            <h2>About CLARITY</h2>
            <p>
              CLARITY is a deterministic, GPU-accelerated evaluation instrument
              for measuring the robustness and evidence stability of multimodal
              clinical AI systems under structured perturbation sweeps.
            </p>
            <ul>
              <li>✓ Deterministic perturbation sweeps</li>
              <li>✓ Evidence Stability Index (ESI)</li>
              <li>✓ Justification drift metrics</li>
              <li>✓ Counterfactual region probing</li>
              <li>✓ Reproducible robustness surfaces</li>
            </ul>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <span className="mono text-secondary">
          CLARITY v0.0.10 — MedGemma Impact Challenge
        </span>
      </footer>
    </div>
  );
}

export default Home;

