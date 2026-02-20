#!/usr/bin/env python
"""Fake R2L CLI for CLARITY testing.

This script simulates the R2L CLI for testing purposes. It is designed to be
invoked by the R2LRunner during tests, writing deterministic artifacts that
can be validated.

USAGE:
    python fake_r2l.py --config <path> --output <dir> [--adapter <name>] [--seed <int>]

BEHAVIOR:
    - Writes deterministic manifest.json and trace_pack.jsonl to output dir
    - All output is reproducible given the same seed
    - Exit code is 0 on success

SPECIAL MODES (controlled by config file content):
    - If config contains "fail": true, exits with code 1
    - If config contains "timeout": true, sleeps for 10 seconds (for timeout tests)
    - If config contains "no_manifest": true, does not write manifest.json
    - If config contains "no_trace": true, does not write trace_pack.jsonl

This fixture is Python-only (no bash) per M03 locked constraints.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def create_deterministic_manifest(
    config_path: Path,
    output_dir: Path,
    adapter: str | None,
    seed: int,
) -> dict:
    """Create a deterministic manifest dictionary.

    The manifest is fully deterministic given the input parameters.
    No random values, no datetime.now(), no uuid4().
    """
    return {
        "version": "1.0.0",
        "run_id": f"fake-run-seed-{seed}",
        "timestamp": "2026-01-01T00:00:00Z",  # Fixed timestamp for determinism
        "seed": seed,
        "r2l_version": "0.1.0-fake",
        "model_id": adapter or "default-adapter",
        "config": str(config_path.name),
        "status": "completed",
        "artifacts": [
            "manifest.json",
            "trace_pack.jsonl",
        ],
    }


def create_deterministic_trace_pack(seed: int) -> list[dict]:
    """Create deterministic trace pack records.

    The trace pack is fully deterministic given the seed.
    No random values, no datetime.now(), no uuid4().
    """
    return [
        {
            "trace_id": f"trace-{seed}-001",
            "step": 1,
            "event": "inference_start",
            "model_id": "fake-model",
        },
        {
            "trace_id": f"trace-{seed}-001",
            "step": 2,
            "event": "inference_complete",
            "output": f"Deterministic output for seed {seed}",
        },
        {
            "trace_id": f"trace-{seed}-001",
            "step": 3,
            "event": "evaluation_complete",
            "metrics": {"accuracy": 1.0},
        },
    ]


def main() -> int:
    """Main entry point for fake R2L CLI."""
    parser = argparse.ArgumentParser(description="Fake R2L CLI for testing")
    parser.add_argument("--config", type=Path, required=True, help="Config file path")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--adapter", type=str, default=None, help="Adapter name")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    # Read config to check for special test modes
    config_data: dict = {}
    if args.config.exists():
        try:
            with open(args.config, encoding="utf-8") as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            # If config is invalid, proceed with empty config
            pass

    # Handle special test modes
    if config_data.get("fail"):
        print("FAKE R2L: Simulated failure", file=sys.stderr)
        return 1

    if config_data.get("timeout"):
        # Sleep long enough to trigger timeout in tests
        # Tests should use short timeouts (e.g., 1 second)
        time.sleep(10)
        return 0

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    # Write manifest unless suppressed
    if not config_data.get("no_manifest"):
        manifest = create_deterministic_manifest(
            args.config, args.output, args.adapter, args.seed
        )
        manifest_path = args.output / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            # Use sorted keys for deterministic output
            json.dump(manifest, f, sort_keys=True, indent=2)

    # Write trace pack unless suppressed
    if not config_data.get("no_trace"):
        traces = create_deterministic_trace_pack(args.seed)
        trace_path = args.output / "trace_pack.jsonl"
        with open(trace_path, "w", encoding="utf-8") as f:
            for record in traces:
                # Use sorted keys for deterministic output
                f.write(json.dumps(record, sort_keys=True) + "\n")

    # Print success message to stdout
    print(f"FAKE R2L: Run completed successfully")
    print(f"FAKE R2L: Config: {args.config}")
    print(f"FAKE R2L: Output: {args.output}")
    print(f"FAKE R2L: Adapter: {args.adapter}")
    print(f"FAKE R2L: Seed: {args.seed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

