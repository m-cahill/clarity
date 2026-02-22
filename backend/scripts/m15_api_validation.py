"""M15 Backend API Validation Script.

Tests that the backend can correctly load and serve M15 real artifacts.

Run from backend directory:
    python -m scripts.m15_api_validation
"""

from __future__ import annotations

import json
import sys

from app.demo_router import _list_cases, _load_json_artifact, verify_artifact_integrity


def main() -> int:
    """Run API validation tests."""
    print("=" * 60)
    print("M15 Backend API Validation")
    print("=" * 60)
    print()

    errors = []

    # Test 1: Case listing
    print("Test 1: Case listing...")
    try:
        cases = _list_cases()
        case_ids = [c.case_id for c in cases]
        print(f"  Found {len(cases)} cases: {case_ids}")

        if "case_m15_real" not in case_ids:
            errors.append("case_m15_real not found in case list")
            print("  [FAIL] case_m15_real not found")
        else:
            print("  [PASS] case_m15_real found")
    except Exception as e:
        errors.append(f"Case listing failed: {e}")
        print(f"  [FAIL] {e}")

    print()

    # Test 2: Manifest loading
    print("Test 2: Manifest loading...")
    try:
        manifest = _load_json_artifact("case_m15_real", "manifest.json")
        print(f"  case_id: {manifest.get('case_id')}")
        print(f"  synthetic: {manifest.get('synthetic')}")
        print(f"  rich_mode: {manifest.get('rich_mode')}")

        if manifest.get("synthetic") is not False:
            errors.append("Manifest synthetic flag should be False")
            print("  [FAIL] synthetic should be False")
        else:
            print("  [PASS] Manifest loaded correctly")
    except Exception as e:
        errors.append(f"Manifest loading failed: {e}")
        print(f"  [FAIL] {e}")

    print()

    # Test 3: Robustness surface loading
    print("Test 3: Robustness surface loading...")
    try:
        surface = _load_json_artifact("case_m15_real", "robustness_surface.json")
        axes = surface.get("axes", [])
        print(f"  axes count: {len(axes)}")
        print(f"  global_mean_esi: {surface.get('global_mean_esi')}")
        print(f"  global_mean_drift: {surface.get('global_mean_drift')}")

        if len(axes) != 2:
            errors.append(f"Expected 2 axes, got {len(axes)}")
            print(f"  [FAIL] Expected 2 axes")
        else:
            # Validate axis structure
            for axis in axes:
                axis_name = axis.get("axis")
                points = axis.get("points", [])
                print(f"    axis '{axis_name}': {len(points)} points")

                # Check for required fields
                required = ["axis", "mean_drift", "mean_esi", "points", "variance_drift", "variance_esi"]
                missing = [f for f in required if f not in axis]
                if missing:
                    errors.append(f"Axis {axis_name} missing fields: {missing}")

            print("  [PASS] Robustness surface loaded correctly")
    except Exception as e:
        errors.append(f"Robustness surface loading failed: {e}")
        print(f"  [FAIL] {e}")

    print()

    # Test 4: Metrics loading
    print("Test 4: Metrics loading...")
    try:
        metrics = _load_json_artifact("case_m15_real", "metrics.json")
        print(f"  baseline_id: {metrics.get('baseline_id')}")
        print(f"  global_mean_csi: {metrics.get('global_mean_csi')}")
        print(f"  monte_carlo samples: {metrics.get('monte_carlo', {}).get('n_samples')}")

        # Validate no None values in critical fields
        csi = metrics.get("global_mean_csi")
        if csi is None:
            errors.append("global_mean_csi is None")
        print("  [PASS] Metrics loaded correctly")
    except Exception as e:
        errors.append(f"Metrics loading failed: {e}")
        print(f"  [FAIL] {e}")

    print()

    # Test 5: Overlay bundle loading
    print("Test 5: Overlay bundle loading...")
    try:
        overlay = _load_json_artifact("case_m15_real", "overlay_bundle.json")
        print(f"  evidence_map width: {overlay.get('evidence_map', {}).get('width')}")
        print(f"  regions count: {len(overlay.get('regions', []))}")
        print("  [PASS] Overlay bundle loaded correctly")
    except Exception as e:
        errors.append(f"Overlay bundle loading failed: {e}")
        print(f"  [FAIL] {e}")

    print()

    # Test 6: Checksum verification
    print("Test 6: Checksum verification...")
    try:
        results = verify_artifact_integrity("case_m15_real")
        print(f"  Verified files: {list(results.keys())}")
        all_valid = all(results.values())
        for filename, valid in results.items():
            status = "[OK]" if valid else "[FAIL]"
            print(f"    {status} {filename}")

        if all_valid:
            print("  [PASS] All checksums valid")
        else:
            invalid = [f for f, v in results.items() if not v]
            errors.append(f"Invalid checksums: {invalid}")
            print("  [FAIL] Some checksums invalid")
    except Exception as e:
        errors.append(f"Checksum verification failed: {e}")
        print(f"  [FAIL] {e}")

    print()

    # Test 7: No NaN values in surfaces
    print("Test 7: NaN value check...")
    try:
        surface = _load_json_artifact("case_m15_real", "robustness_surface.json")

        def check_nan(obj, path=""):
            """Recursively check for NaN values."""
            if isinstance(obj, float):
                import math
                if math.isnan(obj):
                    return [path]
                return []
            elif isinstance(obj, dict):
                nans = []
                for k, v in obj.items():
                    nans.extend(check_nan(v, f"{path}.{k}"))
                return nans
            elif isinstance(obj, list):
                nans = []
                for i, v in enumerate(obj):
                    nans.extend(check_nan(v, f"{path}[{i}]"))
                return nans
            return []

        nan_paths = check_nan(surface)
        if nan_paths:
            errors.append(f"NaN values found at: {nan_paths}")
            print(f"  [FAIL] NaN values found at {nan_paths}")
        else:
            print("  [PASS] No NaN values in robustness surface")
    except Exception as e:
        errors.append(f"NaN check failed: {e}")
        print(f"  [FAIL] {e}")

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print("ALL TESTS PASSED")
        print()
        print("Backend API validation complete.")
        print("Real M15 artifacts load correctly through demo router.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
