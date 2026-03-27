"""Self-identifying `sweep_manifest.json` producer family tokens (readiness).

See `docs/readiness/CLARITY_ARTIFACT_CONTRACT.md` §6.1. Downstream consumers
should read `manifest_schema_family` to select parsing logic without repo-specific
heuristics.
"""

from __future__ import annotations

from typing import Any

# JSON object key (stable contract name)
MANIFEST_SCHEMA_FAMILY = "manifest_schema_family"

# Canonical producer families written by this repository
FAMILY_SWEEP_ORCHESTRATOR_V1 = "clarity_sweep_orchestrator_v1"
FAMILY_RICH_AGGREGATE_V1 = "clarity_rich_aggregate_v1"

KNOWN_MANIFEST_SCHEMA_FAMILIES = frozenset(
    {
        FAMILY_SWEEP_ORCHESTRATOR_V1,
        FAMILY_RICH_AGGREGATE_V1,
    }
)


def parse_manifest_schema_family(obj: dict[str, Any]) -> str | None:
    """Return the canonical family token if present and valid, else ``None``."""
    raw = obj.get(MANIFEST_SCHEMA_FAMILY)
    if not isinstance(raw, str):
        return None
    stripped = raw.strip()
    return stripped if stripped in KNOWN_MANIFEST_SCHEMA_FAMILIES else None


def classify_sweep_manifest_json(obj: dict[str, Any]) -> str:
    """Resolve producer family for parsing.

    Prefer explicit ``manifest_schema_family`` (required for all new CLARITY
    outputs). If absent or invalid, apply a **legacy** heuristic so older
    fixtures and pre-M25 bundles remain interpretable.
    """
    explicit = parse_manifest_schema_family(obj)
    if explicit is not None:
        return explicit

    # Legacy heuristic (pre-self-identification): orchestrator vs aggregate scripts
    runs = obj.get("runs")
    results = obj.get("results")
    if isinstance(runs, list) and "axes" in obj and "results" not in obj:
        return FAMILY_SWEEP_ORCHESTRATOR_V1
    if isinstance(results, list):
        return FAMILY_RICH_AGGREGATE_V1
    return "unknown"
