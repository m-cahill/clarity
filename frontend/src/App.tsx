import { HealthIndicator } from "./HealthIndicator";
import "./App.css";

/**
 * CLARITY Frontend Application
 *
 * M00: Minimal skeleton with health indicator.
 * Demonstrates E2E connectivity to backend.
 */
function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">CLARITY</h1>
        <p className="app-subtitle">
          Clinical Localization and Reasoning Integrity Testing
        </p>
      </header>

      <main className="app-main">
        <section className="status-section">
          <HealthIndicator />
        </section>

        <section className="info-section">
          <div className="info-card">
            <h2>M00 — Bootstrap Complete</h2>
            <p>
              This is the minimal CLARITY frontend skeleton. The health
              indicator above verifies end-to-end connectivity with the backend
              service.
            </p>
            <ul>
              <li>✓ React + Vite + TypeScript</li>
              <li>✓ Backend health check</li>
              <li>✓ Deterministic UI state</li>
            </ul>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <span className="mono text-secondary">
          CLARITY v0.0.1 — MedGemma Impact Challenge
        </span>
      </footer>
    </div>
  );
}

export default App;

