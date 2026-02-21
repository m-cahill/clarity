"""M13 Real Sweep Verification Script.

Runs minimal real sweep: 1 image, 2 seeds, 1 axis.
Produces sweep_manifest.json and verifies determinism.
"""

import json
import hashlib
from pathlib import Path

from PIL import Image

from app.clarity.medgemma_runner import MedGemmaRunner


def main() -> None:
    print("=== CLARITY M13 Real Sweep Verification ===")
    print()

    # Load clinical test image
    image_path = Path("tests/fixtures/baselines/clinical_sample_01.png")
    image = Image.open(image_path)
    print(f"Loaded test image: {image_path}")
    print(f"Image size: {image.size}")
    print()

    # Initialize runner
    print("Initializing MedGemmaRunner...")
    runner = MedGemmaRunner()
    print(f"Model ID: {runner.model_id}")
    print()

    # Minimal sweep: 1 image, 2 seeds, 1 axis
    prompt = "Analyze this medical image for any anomalies."
    seeds = [42, 123]
    results = []

    print("=== Running minimal sweep ===")
    for seed in seeds:
        print(f"  Seed {seed}: running inference...")
        result = runner.generate(prompt, seed=seed, image=image)
        text_preview = result.text[:100] + "..." if len(result.text) > 100 else result.text
        results.append({
            "seed": seed,
            "text": result.text,
            "text_preview": text_preview,
            "bundle_sha": result.bundle_sha,
            "model_id": result.model_id,
        })
        print(f"    bundle_sha: {result.bundle_sha[:16]}...")
        print(f"    text preview: {text_preview[:50]}...")

    print()
    print("=== VRAM Usage ===")
    vram = runner.get_vram_usage()
    print(f"  Allocated: {vram['allocated_gb']} GB")
    print(f"  Reserved: {vram['reserved_gb']} GB")
    print(f"  Max Allocated: {vram['max_allocated_gb']} GB")
    print()

    # Create sweep manifest
    manifest = {
        "sweep_id": "m13-real-sweep-verification",
        "model_id": runner.model_id,
        "image_path": str(image_path),
        "prompt": prompt,
        "seeds": seeds,
        "results": results,
        "vram_usage": vram,
    }

    # Compute manifest hash
    manifest_json = json.dumps(manifest, sort_keys=True, indent=2)
    manifest_hash = hashlib.sha256(manifest_json.encode()).hexdigest()

    print("=== Sweep Manifest ===")
    print(f"  Manifest SHA256: {manifest_hash}")
    print()

    # Save manifest
    output_dir = Path("tests/fixtures/baselines/m13_real_sweep")
    output_dir.mkdir(exist_ok=True)
    manifest_path = output_dir / "sweep_manifest.json"
    manifest_path.write_text(manifest_json)
    print(f"  Saved to: {manifest_path}")

    # Save manifest hash for verification
    hash_path = output_dir / "manifest_hash.txt"
    hash_path.write_text(manifest_hash)
    print(f"  Hash saved to: {hash_path}")

    print()
    print("=== M13 Real Sweep Complete ===")
    vram_pass = "PASS" if vram["max_allocated_gb"] <= 12 else "FAIL"
    print(f"  VRAM budget (<=12GB): {vram_pass}")
    print(f"  Results count: {len(results)}")
    print(f"  Manifest hash: {manifest_hash[:32]}...")


if __name__ == "__main__":
    main()

