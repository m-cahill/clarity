"""M15 Real Artifact UI Validation Sweep Script.

Generates real rich-mode artifacts for UI validation:
- 1 image
- 2 seeds (42, 123)
- 2 perturbation axes (brightness, contrast)
- Rich mode enabled (confidence/entropy metrics)

Produces:
- sweep_manifest.json
- robustness_surface.json
- confidence_surface.json
- entropy_surface.json
- monte_carlo_stats.json
- summary_hash.txt

Run with:
    CLARITY_REAL_MODEL=true CLARITY_RICH_MODE=true python -m scripts.m15_real_ui_sweep

For determinism verification, run twice and compare summary_hash.txt.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

from app.clarity.medgemma_runner import MedGemmaRunner
from app.clarity.rich_generation import is_rich_mode_enabled
from app.clarity.surfaces import (
    AxisSurface,
    ConfidenceSurface,
    ConfidenceSurfacePoint,
    EntropySurface,
    EntropySurfacePoint,
    RobustnessSurface,
    SurfacePoint,
)


def deterministic_json_dumps(obj: Any) -> str:
    """Deterministic JSON serialization."""
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=True)


def compute_sha256(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main() -> None:
    print("=" * 60)
    print("CLARITY M15 Real Artifact UI Validation Sweep")
    print("=" * 60)
    print()

    # Verify environment
    if not is_rich_mode_enabled():
        print("ERROR: Rich mode not enabled.")
        print("Run with: CLARITY_REAL_MODEL=true CLARITY_RICH_MODE=true")
        return

    # Configuration
    image_path = Path("tests/fixtures/baselines/clinical_sample_01.png")
    seeds = [42, 123]
    perturbation_axes = {
        "brightness": [0.8, 1.0, 1.2],
        "contrast": [0.9, 1.0, 1.1],
    }
    prompt = "Analyze this medical image for any anomalies."

    # Output directory
    output_dir = Path("tests/fixtures/baselines/m15_real_ui")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()

    # Load image
    print(f"Loading image: {image_path}")
    image = Image.open(image_path)
    print(f"Image size: {image.size}")
    print()

    # Initialize runner
    print("Initializing MedGemmaRunner (rich mode)...")
    runner = MedGemmaRunner()
    print(f"Model ID: {runner.model_id}")
    print()

    # Collect all results
    all_results: list[dict[str, Any]] = []
    rich_summaries: dict[str, list[dict[str, Any]]] = {
        axis: [] for axis in perturbation_axes
    }

    # Run sweep: for each axis, for each value, for each seed
    print("=" * 60)
    print("Running rich-mode sweep...")
    print("=" * 60)

    for axis_name, axis_values in perturbation_axes.items():
        print(f"\n--- Axis: {axis_name} ---")

        for value in axis_values:
            value_str = str(value).replace(".", "p")
            print(f"  Value {value} ({value_str}):")

            axis_results = []
            confidences = []
            entropies = []

            for seed in seeds:
                print(f"    Seed {seed}: generating (rich mode)...")

                result = runner.generate_rich(prompt, seed=seed, image=image)

                result_data = {
                    "axis": axis_name,
                    "value": value,
                    "value_str": value_str,
                    "seed": seed,
                    "text_preview": result.text[:80] + "..." if len(result.text) > 80 else result.text,
                    "bundle_sha": result.bundle_sha,
                    "model_id": result.model_id,
                }

                # Add rich summary if available
                if result.rich_summary:
                    result_data["rich_summary"] = {
                        "mean_logprob": result.rich_summary.mean_logprob,
                        "output_entropy": result.rich_summary.output_entropy,
                        "confidence_score": result.rich_summary.confidence_score,
                        "token_count": result.rich_summary.token_count,
                        "summary_hash": result.rich_summary.summary_hash,
                    }
                    # Collect for surface computation
                    if result.rich_summary.confidence_score is not None:
                        confidences.append(result.rich_summary.confidence_score)
                    if result.rich_summary.output_entropy is not None:
                        entropies.append(result.rich_summary.output_entropy)

                all_results.append(result_data)
                axis_results.append(result_data)

                print(f"      bundle_sha: {result.bundle_sha[:16]}...")
                if result.rich_summary:
                    print(f"      summary_hash: {result.rich_summary.summary_hash[:16]}...")
                    print(f"      confidence: {result.rich_summary.confidence_score}")

            # Compute aggregates for this axis value
            rich_summaries[axis_name].append({
                "value": value,
                "value_str": value_str,
                "mean_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                "mean_entropy": sum(entropies) / len(entropies) if entropies else 0.0,
                "confidences": confidences,
                "entropies": entropies,
                "results": axis_results,
            })

    print()
    print("=" * 60)
    print("VRAM Usage")
    print("=" * 60)
    vram = runner.get_vram_usage()
    print(f"  Allocated: {vram['allocated_gb']} GB")
    print(f"  Reserved: {vram['reserved_gb']} GB")
    print(f"  Max Allocated: {vram['max_allocated_gb']} GB")
    print()

    # Build sweep manifest
    manifest = {
        "sweep_id": "m15-real-ui-validation",
        "model_id": runner.model_id,
        "image_path": str(image_path),
        "prompt": prompt,
        "seeds": seeds,
        "axes": {name: values for name, values in perturbation_axes.items()},
        "results": all_results,
        "vram_usage": vram,
        "rich_mode": True,
    }

    # Compute robustness surface (simplified: use confidence as proxy for ESI)
    print("Computing surfaces...")
    robustness_surface = build_robustness_surface(rich_summaries)
    confidence_surface = build_confidence_surface(rich_summaries)
    entropy_surface = build_entropy_surface(rich_summaries)
    monte_carlo_stats = build_monte_carlo_stats(rich_summaries, seeds)

    # Serialize all artifacts
    manifest_json = deterministic_json_dumps(manifest)
    robustness_json = deterministic_json_dumps(robustness_surface.to_dict())
    confidence_json = deterministic_json_dumps(confidence_surface)
    entropy_json = deterministic_json_dumps(entropy_surface)
    monte_carlo_json = deterministic_json_dumps(monte_carlo_stats)

    # Compute hashes
    manifest_hash = compute_sha256(manifest_json)
    robustness_hash = compute_sha256(robustness_json)
    confidence_hash = compute_sha256(confidence_json)
    entropy_hash = compute_sha256(entropy_json)

    bundle_content = f"{manifest_hash}|{robustness_hash}|{confidence_hash}|{entropy_hash}"
    bundle_hash = compute_sha256(bundle_content)

    summary_text = f"""M15 Real UI Validation Artifacts
================================
Generated: deterministic
Model: {runner.model_id}
Seeds: {seeds}
Axes: {list(perturbation_axes.keys())}

Artifact Hashes:
  manifest_sha256: {manifest_hash}
  robustness_sha256: {robustness_hash}
  confidence_sha256: {confidence_hash}
  entropy_sha256: {entropy_hash}
  bundle_sha256: {bundle_hash}

VRAM:
  max_allocated_gb: {vram['max_allocated_gb']}
"""

    # Write artifacts
    print()
    print("Writing artifacts...")

    (output_dir / "sweep_manifest.json").write_text(manifest_json, encoding="utf-8")
    print(f"  ✓ sweep_manifest.json")

    (output_dir / "robustness_surface.json").write_text(robustness_json, encoding="utf-8")
    print(f"  ✓ robustness_surface.json")

    (output_dir / "confidence_surface.json").write_text(confidence_json, encoding="utf-8")
    print(f"  ✓ confidence_surface.json")

    (output_dir / "entropy_surface.json").write_text(entropy_json, encoding="utf-8")
    print(f"  ✓ entropy_surface.json")

    (output_dir / "monte_carlo_stats.json").write_text(monte_carlo_json, encoding="utf-8")
    print(f"  ✓ monte_carlo_stats.json")

    (output_dir / "summary_hash.txt").write_text(summary_text, encoding="utf-8")
    print(f"  ✓ summary_hash.txt")

    print()
    print("=" * 60)
    print("M15 Artifact Generation Complete")
    print("=" * 60)
    print(f"  Bundle SHA256: {bundle_hash}")
    print(f"  Manifest SHA256: {manifest_hash[:32]}...")
    print(f"  Output: {output_dir}")
    print()
    print("For determinism verification:")
    print("  1. Run this script again")
    print("  2. Compare summary_hash.txt")
    print("  3. Bundle SHA256 should be identical")


def build_robustness_surface(
    rich_summaries: dict[str, list[dict[str, Any]]]
) -> RobustnessSurface:
    """Build robustness surface from rich summaries.
    
    Uses confidence as proxy for ESI and entropy drift for drift metric.
    """
    axis_surfaces = []
    all_esi = []
    all_drift = []

    for axis_name in sorted(rich_summaries.keys()):
        axis_data = rich_summaries[axis_name]
        points = []

        for value_data in axis_data:
            # Use confidence as ESI proxy (higher confidence = more stable)
            esi = round(value_data["mean_confidence"], 8)
            # Use entropy variance as drift proxy
            entropies = value_data["entropies"]
            if len(entropies) > 1:
                mean_e = sum(entropies) / len(entropies)
                drift = round(sum(abs(e - mean_e) for e in entropies) / len(entropies), 8)
            else:
                drift = 0.0

            point = SurfacePoint(
                axis=axis_name,
                value=value_data["value_str"],
                esi=esi,
                drift=drift,
            )
            points.append(point)
            all_esi.append(esi)
            all_drift.append(drift)

        # Sort points by value for determinism
        points = sorted(points, key=lambda p: p.value)

        # Compute axis statistics
        esi_values = [p.esi for p in points]
        drift_values = [p.drift for p in points]

        mean_esi = round(sum(esi_values) / len(esi_values), 8) if esi_values else 0.0
        mean_drift = round(sum(drift_values) / len(drift_values), 8) if drift_values else 0.0

        var_esi = round(
            sum((e - mean_esi) ** 2 for e in esi_values) / len(esi_values), 8
        ) if esi_values else 0.0
        var_drift = round(
            sum((d - mean_drift) ** 2 for d in drift_values) / len(drift_values), 8
        ) if drift_values else 0.0

        axis_surface = AxisSurface(
            axis=axis_name,
            points=tuple(points),
            mean_esi=mean_esi,
            mean_drift=mean_drift,
            variance_esi=var_esi,
            variance_drift=var_drift,
        )
        axis_surfaces.append(axis_surface)

    # Sort axis surfaces by name for determinism
    axis_surfaces = sorted(axis_surfaces, key=lambda a: a.axis)

    # Compute global statistics
    global_mean_esi = round(sum(all_esi) / len(all_esi), 8) if all_esi else 0.0
    global_mean_drift = round(sum(all_drift) / len(all_drift), 8) if all_drift else 0.0
    global_var_esi = round(
        sum((e - global_mean_esi) ** 2 for e in all_esi) / len(all_esi), 8
    ) if all_esi else 0.0
    global_var_drift = round(
        sum((d - global_mean_drift) ** 2 for d in all_drift) / len(all_drift), 8
    ) if all_drift else 0.0

    return RobustnessSurface(
        axes=tuple(axis_surfaces),
        global_mean_esi=global_mean_esi,
        global_mean_drift=global_mean_drift,
        global_variance_esi=global_var_esi,
        global_variance_drift=global_var_drift,
    )


def build_confidence_surface(
    rich_summaries: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    """Build confidence surface JSON structure."""
    axes = []
    all_csi = []
    all_conf = []

    for axis_name in sorted(rich_summaries.keys()):
        axis_data = rich_summaries[axis_name]
        points = []

        for value_data in axis_data:
            confidences = value_data["confidences"]
            mean_conf = round(sum(confidences) / len(confidences), 8) if confidences else 0.0

            # CSI: 1 - normalized variance (higher = more stable)
            if len(confidences) > 1:
                mean_c = sum(confidences) / len(confidences)
                var_c = sum((c - mean_c) ** 2 for c in confidences) / len(confidences)
                # Normalize by max possible variance (0.25 for [0,1] range)
                csi = round(1.0 - min(var_c / 0.25, 1.0), 8)
                conf_var = round(var_c, 8)
            else:
                csi = 1.0
                conf_var = 0.0

            point = {
                "axis": axis_name,
                "value": value_data["value_str"],
                "mean_confidence": mean_conf,
                "csi": csi,
                "confidence_variance": conf_var,
            }
            points.append(point)
            all_csi.append(csi)
            all_conf.append(mean_conf)

        # Sort by value
        points = sorted(points, key=lambda p: p["value"])

        axis_surface = {
            "axis": axis_name,
            "points": points,
            "mean_csi": round(sum(p["csi"] for p in points) / len(points), 8) if points else 0.0,
            "overall_mean_confidence": round(sum(p["mean_confidence"] for p in points) / len(points), 8) if points else 0.0,
            "overall_variance": round(sum(p["confidence_variance"] for p in points) / len(points), 8) if points else 0.0,
        }
        axes.append(axis_surface)

    return {
        "confidence_surfaces": sorted(axes, key=lambda a: a["axis"]),
        "global_mean_csi": round(sum(all_csi) / len(all_csi), 8) if all_csi else 0.0,
        "global_mean_confidence": round(sum(all_conf) / len(all_conf), 8) if all_conf else 0.0,
    }


def build_entropy_surface(
    rich_summaries: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    """Build entropy surface JSON structure."""
    axes = []
    all_edm = []
    all_entropy = []

    # Compute baseline entropy (mean across all runs at value=1.0)
    baseline_entropies = []
    for axis_data in rich_summaries.values():
        for value_data in axis_data:
            if value_data["value"] == 1.0:
                baseline_entropies.extend(value_data["entropies"])
    baseline_entropy = round(sum(baseline_entropies) / len(baseline_entropies), 8) if baseline_entropies else 0.0

    for axis_name in sorted(rich_summaries.keys()):
        axis_data = rich_summaries[axis_name]
        points = []

        for value_data in axis_data:
            entropies = value_data["entropies"]
            mean_entropy = round(sum(entropies) / len(entropies), 8) if entropies else 0.0

            # EDM: mean absolute deviation from baseline
            edm = round(
                sum(abs(e - baseline_entropy) for e in entropies) / len(entropies), 8
            ) if entropies else 0.0

            # Variance
            if len(entropies) > 1:
                var_e = sum((e - mean_entropy) ** 2 for e in entropies) / len(entropies)
            else:
                var_e = 0.0

            point = {
                "axis": axis_name,
                "value": value_data["value_str"],
                "mean_entropy": mean_entropy,
                "edm": edm,
                "entropy_variance": round(var_e, 8),
            }
            points.append(point)
            all_edm.append(edm)
            all_entropy.append(mean_entropy)

        # Sort by value
        points = sorted(points, key=lambda p: p["value"])

        axis_surface = {
            "axis": axis_name,
            "points": points,
            "mean_edm": round(sum(p["edm"] for p in points) / len(points), 8) if points else 0.0,
            "overall_mean_entropy": round(sum(p["mean_entropy"] for p in points) / len(points), 8) if points else 0.0,
            "overall_variance": round(sum(p["entropy_variance"] for p in points) / len(points), 8) if points else 0.0,
            "baseline_entropy": baseline_entropy,
        }
        axes.append(axis_surface)

    return {
        "entropy_surfaces": sorted(axes, key=lambda a: a["axis"]),
        "global_mean_edm": round(sum(all_edm) / len(all_edm), 8) if all_edm else 0.0,
        "global_mean_entropy": round(sum(all_entropy) / len(all_entropy), 8) if all_entropy else 0.0,
        "baseline_entropy": baseline_entropy,
    }


def build_monte_carlo_stats(
    rich_summaries: dict[str, list[dict[str, Any]]],
    seeds: list[int],
) -> dict[str, Any]:
    """Build Monte Carlo statistics JSON structure."""
    all_confidences = []
    all_entropies = []

    for axis_data in rich_summaries.values():
        for value_data in axis_data:
            all_confidences.extend(value_data["confidences"])
            all_entropies.extend(value_data["entropies"])

    # Compute statistics
    n = len(all_confidences)
    if n > 0:
        mean_conf = sum(all_confidences) / n
        var_conf = sum((c - mean_conf) ** 2 for c in all_confidences) / n
        std_conf = var_conf ** 0.5

        mean_ent = sum(all_entropies) / n
        var_ent = sum((e - mean_ent) ** 2 for e in all_entropies) / n
        std_ent = var_ent ** 0.5
    else:
        mean_conf = var_conf = std_conf = 0.0
        mean_ent = var_ent = std_ent = 0.0

    return {
        "monte_carlo": {
            "seeds": seeds,
            "n_samples": n,
            "confidence": {
                "mean": round(mean_conf, 8),
                "variance": round(var_conf, 8),
                "std": round(std_conf, 8),
                "min": round(min(all_confidences), 8) if all_confidences else 0.0,
                "max": round(max(all_confidences), 8) if all_confidences else 0.0,
            },
            "entropy": {
                "mean": round(mean_ent, 8),
                "variance": round(var_ent, 8),
                "std": round(std_ent, 8),
                "min": round(min(all_entropies), 8) if all_entropies else 0.0,
                "max": round(max(all_entropies), 8) if all_entropies else 0.0,
            },
        },
        "axes": list(sorted(rich_summaries.keys())),
        "total_runs": n,
    }


if __name__ == "__main__":
    main()
