/**
 * Demo Mode Banner Component.
 *
 * Displays a prominent banner when the app is running in demo mode
 * to clearly indicate that data is synthetic/precomputed.
 */

import { isDemoMode } from "./api";
import "./DemoBanner.css";

export function DemoBanner() {
  if (!isDemoMode()) {
    return null;
  }

  return (
    <div className="demo-banner" role="alert" aria-live="polite">
      <span className="demo-banner-icon">⚠️</span>
      <span className="demo-banner-text">
        <strong>Demo Mode</strong> — Precomputed Artifacts (Synthetic)
      </span>
    </div>
  );
}

export default DemoBanner;

