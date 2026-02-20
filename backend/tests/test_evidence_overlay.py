"""Tests for the evidence_overlay module (M10).

This module contains tests for:
- EvidenceMap creation and validation
- Heatmap normalization
- Region extraction via threshold + BFS
- OverlayBundle creation
- Determinism verification
- Edge cases and error handling
- AST guardrails (no forbidden imports)
"""

import ast
import math
from pathlib import Path

import pytest

from app.clarity.evidence_overlay import (
    DEFAULT_EVIDENCE_HEIGHT,
    DEFAULT_EVIDENCE_WIDTH,
    EVIDENCE_THRESHOLD,
    EvidenceMap,
    EvidenceOverlayEngine,
    EvidenceOverlayError,
    Heatmap,
    OverlayBundle,
    OverlayRegion,
    create_overlay_bundle,
    extract_regions_from_heatmap,
    generate_stubbed_evidence_map,
    normalize_evidence_to_heatmap,
)


# =============================================================================
# EvidenceMap Tests
# =============================================================================


class TestEvidenceMap:
    """Tests for EvidenceMap dataclass."""

    def test_evidence_map_creation_valid(self) -> None:
        """Test creating a valid EvidenceMap."""
        values = ((0.1, 0.2), (0.3, 0.4))
        evidence = EvidenceMap(width=2, height=2, values=values)
        assert evidence.width == 2
        assert evidence.height == 2
        assert evidence.values == values

    def test_evidence_map_invalid_width_zero(self) -> None:
        """Test that width=0 raises error."""
        with pytest.raises(EvidenceOverlayError, match="Invalid dimensions"):
            EvidenceMap(width=0, height=2, values=())

    def test_evidence_map_invalid_height_zero(self) -> None:
        """Test that height=0 raises error."""
        with pytest.raises(EvidenceOverlayError, match="Invalid dimensions"):
            EvidenceMap(width=2, height=0, values=())

    def test_evidence_map_invalid_negative_dimensions(self) -> None:
        """Test that negative dimensions raise error."""
        with pytest.raises(EvidenceOverlayError, match="Invalid dimensions"):
            EvidenceMap(width=-1, height=2, values=())

    def test_evidence_map_height_mismatch(self) -> None:
        """Test that height mismatch raises error."""
        values = ((0.1, 0.2),)  # Only 1 row, but height=2
        with pytest.raises(EvidenceOverlayError, match="height mismatch"):
            EvidenceMap(width=2, height=2, values=values)

    def test_evidence_map_width_mismatch(self) -> None:
        """Test that width mismatch raises error."""
        values = ((0.1,), (0.2,))  # Only 1 col per row, but width=2
        with pytest.raises(EvidenceOverlayError, match="width mismatch"):
            EvidenceMap(width=2, height=2, values=values)

    def test_evidence_map_to_dict(self) -> None:
        """Test to_dict serialization."""
        values = ((0.1, 0.2), (0.3, 0.4))
        evidence = EvidenceMap(width=2, height=2, values=values)
        result = evidence.to_dict()
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["values"] == [[0.1, 0.2], [0.3, 0.4]]

    def test_evidence_map_frozen(self) -> None:
        """Test that EvidenceMap is immutable."""
        values = ((0.1, 0.2), (0.3, 0.4))
        evidence = EvidenceMap(width=2, height=2, values=values)
        with pytest.raises(AttributeError):
            evidence.width = 5  # type: ignore


# =============================================================================
# Heatmap Tests
# =============================================================================


class TestHeatmap:
    """Tests for Heatmap dataclass."""

    def test_heatmap_creation_valid(self) -> None:
        """Test creating a valid Heatmap."""
        values = ((0.0, 0.5), (0.5, 1.0))
        heatmap = Heatmap(width=2, height=2, values=values)
        assert heatmap.width == 2
        assert heatmap.height == 2

    def test_heatmap_invalid_dimensions(self) -> None:
        """Test that invalid dimensions raise error."""
        with pytest.raises(EvidenceOverlayError, match="Invalid dimensions"):
            Heatmap(width=0, height=2, values=())

    def test_heatmap_to_dict(self) -> None:
        """Test to_dict serialization."""
        values = ((0.0, 0.5), (0.5, 1.0))
        heatmap = Heatmap(width=2, height=2, values=values)
        result = heatmap.to_dict()
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["values"] == [[0.0, 0.5], [0.5, 1.0]]


# =============================================================================
# OverlayRegion Tests
# =============================================================================


class TestOverlayRegion:
    """Tests for OverlayRegion dataclass."""

    def test_overlay_region_creation(self) -> None:
        """Test creating an OverlayRegion."""
        region = OverlayRegion(
            region_id="evidence_r0",
            x_min=0.2,
            y_min=0.3,
            x_max=0.5,
            y_max=0.6,
            area=0.09,
        )
        assert region.region_id == "evidence_r0"
        assert region.x_min == 0.2
        assert region.area == 0.09

    def test_overlay_region_to_dict(self) -> None:
        """Test to_dict serialization with alphabetical keys."""
        region = OverlayRegion(
            region_id="evidence_r0",
            x_min=0.2,
            y_min=0.3,
            x_max=0.5,
            y_max=0.6,
            area=0.09,
        )
        result = region.to_dict()
        keys = list(result.keys())
        # Keys should be alphabetically sorted
        assert keys == sorted(keys)
        assert result["area"] == 0.09
        assert result["region_id"] == "evidence_r0"


# =============================================================================
# OverlayBundle Tests
# =============================================================================


class TestOverlayBundle:
    """Tests for OverlayBundle dataclass."""

    def test_overlay_bundle_creation(self) -> None:
        """Test creating an OverlayBundle."""
        evidence = EvidenceMap(width=2, height=2, values=((0.5, 0.5), (0.5, 0.5)))
        heatmap = Heatmap(width=2, height=2, values=((0.5, 0.5), (0.5, 0.5)))
        regions: tuple[OverlayRegion, ...] = ()
        bundle = OverlayBundle(
            evidence_map=evidence,
            heatmap=heatmap,
            regions=regions,
        )
        assert bundle.evidence_map == evidence
        assert bundle.heatmap == heatmap
        assert bundle.regions == ()

    def test_overlay_bundle_to_dict(self) -> None:
        """Test to_dict serialization."""
        evidence = EvidenceMap(width=2, height=2, values=((0.5, 0.5), (0.5, 0.5)))
        heatmap = Heatmap(width=2, height=2, values=((0.5, 0.5), (0.5, 0.5)))
        bundle = OverlayBundle(
            evidence_map=evidence,
            heatmap=heatmap,
            regions=(),
        )
        result = bundle.to_dict()
        assert "evidence_map" in result
        assert "heatmap" in result
        assert "regions" in result
        assert result["regions"] == []


# =============================================================================
# generate_stubbed_evidence_map Tests
# =============================================================================


class TestGenerateStubbedEvidenceMap:
    """Tests for generate_stubbed_evidence_map function."""

    def test_generates_correct_dimensions(self) -> None:
        """Test that generated map has correct dimensions."""
        evidence = generate_stubbed_evidence_map(width=50, height=50, seed=42)
        assert evidence.width == 50
        assert evidence.height == 50
        assert len(evidence.values) == 50
        assert all(len(row) == 50 for row in evidence.values)

    def test_default_dimensions(self) -> None:
        """Test default 224x224 dimensions."""
        evidence = generate_stubbed_evidence_map()
        assert evidence.width == DEFAULT_EVIDENCE_WIDTH
        assert evidence.height == DEFAULT_EVIDENCE_HEIGHT

    def test_values_in_valid_range(self) -> None:
        """Test that all values are in [0, 1]."""
        evidence = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        for row in evidence.values:
            for value in row:
                assert 0.0 <= value <= 1.0

    def test_determinism_same_seed(self) -> None:
        """Test that same seed produces identical results."""
        e1 = generate_stubbed_evidence_map(width=50, height=50, seed=123)
        e2 = generate_stubbed_evidence_map(width=50, height=50, seed=123)
        assert e1.values == e2.values

    def test_different_seeds_produce_different_patterns(self) -> None:
        """Test that different seeds produce different patterns."""
        e1 = generate_stubbed_evidence_map(width=50, height=50, seed=42)
        e2 = generate_stubbed_evidence_map(width=50, height=50, seed=99)
        assert e1.values != e2.values

    def test_values_are_8_decimal_rounded(self) -> None:
        """Test that values are rounded to 8 decimals."""
        evidence = generate_stubbed_evidence_map(width=10, height=10, seed=42)
        for row in evidence.values:
            for value in row:
                # Round to 8 decimals and compare
                assert value == round(value, 8)

    def test_invalid_width_raises_error(self) -> None:
        """Test that invalid width raises error."""
        with pytest.raises(EvidenceOverlayError, match="Invalid dimensions"):
            generate_stubbed_evidence_map(width=0, height=10, seed=42)

    def test_invalid_height_raises_error(self) -> None:
        """Test that invalid height raises error."""
        with pytest.raises(EvidenceOverlayError, match="Invalid dimensions"):
            generate_stubbed_evidence_map(width=10, height=-1, seed=42)

    def test_pattern_has_variation(self) -> None:
        """Test that pattern has meaningful variation (not constant)."""
        evidence = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        all_values = [v for row in evidence.values for v in row]
        min_val = min(all_values)
        max_val = max(all_values)
        # Should have meaningful range
        assert max_val - min_val > 0.1


# =============================================================================
# normalize_evidence_to_heatmap Tests
# =============================================================================


class TestNormalizeEvidenceToHeatmap:
    """Tests for normalize_evidence_to_heatmap function."""

    def test_basic_normalization(self) -> None:
        """Test basic min-max normalization."""
        values = ((0.0, 0.5), (0.5, 1.0))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        assert heatmap.width == 2
        assert heatmap.height == 2

    def test_normalization_produces_0_to_1_range(self) -> None:
        """Test that normalized values are in [0, 1]."""
        values = ((0.2, 0.4), (0.6, 0.8))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        for row in heatmap.values:
            for v in row:
                assert 0.0 <= v <= 1.0

    def test_normalization_min_becomes_0(self) -> None:
        """Test that minimum value becomes 0."""
        values = ((0.3, 0.5), (0.5, 0.7))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        # Find minimum in result
        min_val = min(v for row in heatmap.values for v in row)
        assert min_val == 0.0

    def test_normalization_max_becomes_1(self) -> None:
        """Test that maximum value becomes 1."""
        values = ((0.3, 0.5), (0.5, 0.7))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        # Find maximum in result
        max_val = max(v for row in heatmap.values for v in row)
        assert max_val == 1.0

    def test_constant_values_normalized(self) -> None:
        """Test normalization of constant values."""
        values = ((0.5, 0.5), (0.5, 0.5))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        # All values should be 0.5 (constant)
        for row in heatmap.values:
            for v in row:
                assert v == 0.5

    def test_zero_values_normalized(self) -> None:
        """Test normalization of all-zero values."""
        values = ((0.0, 0.0), (0.0, 0.0))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        # All values should be 0.0
        for row in heatmap.values:
            for v in row:
                assert v == 0.0

    def test_values_rounded_to_8_decimals(self) -> None:
        """Test that normalized values are rounded to 8 decimals."""
        values = ((0.1, 0.2), (0.3, 0.4))
        evidence = EvidenceMap(width=2, height=2, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        for row in heatmap.values:
            for v in row:
                assert v == round(v, 8)

    def test_non_finite_value_raises_error(self) -> None:
        """Test that non-finite values raise error."""
        values = ((0.1, float("inf")), (0.3, 0.4))
        evidence = EvidenceMap(width=2, height=2, values=values)
        with pytest.raises(EvidenceOverlayError, match="Non-finite"):
            normalize_evidence_to_heatmap(evidence)

    def test_nan_value_raises_error(self) -> None:
        """Test that NaN values raise error."""
        values = ((0.1, float("nan")), (0.3, 0.4))
        evidence = EvidenceMap(width=2, height=2, values=values)
        with pytest.raises(EvidenceOverlayError, match="Non-finite"):
            normalize_evidence_to_heatmap(evidence)


# =============================================================================
# extract_regions_from_heatmap Tests
# =============================================================================


class TestExtractRegionsFromHeatmap:
    """Tests for extract_regions_from_heatmap function."""

    def test_no_regions_below_threshold(self) -> None:
        """Test that values below threshold produce no regions."""
        values = ((0.1, 0.2), (0.3, 0.4))
        heatmap = Heatmap(width=2, height=2, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert regions == ()

    def test_all_above_threshold_single_region(self) -> None:
        """Test that all above threshold produces single region."""
        values = ((0.8, 0.9), (0.9, 0.8))
        heatmap = Heatmap(width=2, height=2, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 1
        assert regions[0].region_id == "evidence_r0"

    def test_single_pixel_region(self) -> None:
        """Test extraction of single pixel region."""
        values = ((0.1, 0.9), (0.1, 0.1))
        heatmap = Heatmap(width=2, height=2, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 1

    def test_multiple_disconnected_regions(self) -> None:
        """Test extraction of multiple disconnected regions."""
        values = (
            (0.9, 0.1, 0.9),
            (0.1, 0.1, 0.1),
            (0.9, 0.1, 0.9),
        )
        heatmap = Heatmap(width=3, height=3, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        # Four corners, each is a separate region
        assert len(regions) == 4

    def test_region_bounding_box_correct(self) -> None:
        """Test that region bounding box is computed correctly."""
        values = (
            (0.1, 0.1, 0.1, 0.1),
            (0.1, 0.9, 0.9, 0.1),
            (0.1, 0.9, 0.9, 0.1),
            (0.1, 0.1, 0.1, 0.1),
        )
        heatmap = Heatmap(width=4, height=4, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 1
        region = regions[0]
        # Region should cover middle 2x2 area
        assert region.x_min == 0.25  # col 1 out of 4
        assert region.y_min == 0.25  # row 1 out of 4
        assert region.x_max == 0.75  # col 3 out of 4
        assert region.y_max == 0.75  # row 3 out of 4

    def test_regions_sorted_by_area_descending(self) -> None:
        """Test that regions are sorted by area (descending)."""
        # Create two regions of different sizes
        values = (
            (0.9, 0.9, 0.1, 0.1, 0.1),
            (0.9, 0.9, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.9, 0.1),
            (0.1, 0.1, 0.1, 0.1, 0.1),
        )
        heatmap = Heatmap(width=5, height=5, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 2
        # First region should have larger area
        assert regions[0].area >= regions[1].area

    def test_region_ids_reassigned_after_sorting(self) -> None:
        """Test that region IDs are reassigned after sorting."""
        values = (
            (0.9, 0.1, 0.9),
            (0.1, 0.1, 0.9),
            (0.1, 0.1, 0.9),
        )
        heatmap = Heatmap(width=3, height=3, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        # Check IDs are sequential starting from 0
        for idx, region in enumerate(regions):
            assert region.region_id == f"evidence_r{idx}"

    def test_invalid_threshold_negative(self) -> None:
        """Test that negative threshold raises error."""
        values = ((0.5, 0.5), (0.5, 0.5))
        heatmap = Heatmap(width=2, height=2, values=values)
        with pytest.raises(EvidenceOverlayError, match="Invalid threshold"):
            extract_regions_from_heatmap(heatmap, threshold=-0.1)

    def test_invalid_threshold_above_1(self) -> None:
        """Test that threshold > 1 raises error."""
        values = ((0.5, 0.5), (0.5, 0.5))
        heatmap = Heatmap(width=2, height=2, values=values)
        with pytest.raises(EvidenceOverlayError, match="Invalid threshold"):
            extract_regions_from_heatmap(heatmap, threshold=1.1)

    def test_default_threshold(self) -> None:
        """Test that default threshold is EVIDENCE_THRESHOLD (0.7)."""
        assert EVIDENCE_THRESHOLD == 0.7

    def test_region_area_calculated_correctly(self) -> None:
        """Test that region area is calculated correctly."""
        values = (
            (0.9, 0.9, 0.1, 0.1),
            (0.9, 0.9, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1),
        )
        heatmap = Heatmap(width=4, height=4, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 1
        # Region covers 2x2 out of 4x4 = 0.25 area
        assert abs(regions[0].area - 0.25) < 0.01


# =============================================================================
# create_overlay_bundle Tests
# =============================================================================


class TestCreateOverlayBundle:
    """Tests for create_overlay_bundle function."""

    def test_creates_complete_bundle(self) -> None:
        """Test that bundle contains all components."""
        evidence = generate_stubbed_evidence_map(width=50, height=50, seed=42)
        bundle = create_overlay_bundle(evidence)
        assert bundle.evidence_map == evidence
        assert bundle.heatmap is not None
        assert bundle.regions is not None

    def test_heatmap_dimensions_match_evidence(self) -> None:
        """Test that heatmap has same dimensions as evidence."""
        evidence = generate_stubbed_evidence_map(width=100, height=80, seed=42)
        bundle = create_overlay_bundle(evidence)
        assert bundle.heatmap.width == evidence.width
        assert bundle.heatmap.height == evidence.height

    def test_bundle_serialization(self) -> None:
        """Test that bundle can be serialized to dict."""
        evidence = generate_stubbed_evidence_map(width=50, height=50, seed=42)
        bundle = create_overlay_bundle(evidence)
        result = bundle.to_dict()
        assert "evidence_map" in result
        assert "heatmap" in result
        assert "regions" in result


# =============================================================================
# EvidenceOverlayEngine Tests
# =============================================================================


class TestEvidenceOverlayEngine:
    """Tests for EvidenceOverlayEngine class."""

    def test_engine_generate_stubbed_evidence(self) -> None:
        """Test engine method for generating stubbed evidence."""
        engine = EvidenceOverlayEngine()
        evidence = engine.generate_stubbed_evidence(width=50, height=50, seed=42)
        assert evidence.width == 50
        assert evidence.height == 50

    def test_engine_normalize(self) -> None:
        """Test engine method for normalization."""
        engine = EvidenceOverlayEngine()
        evidence = engine.generate_stubbed_evidence(width=50, height=50, seed=42)
        heatmap = engine.normalize(evidence)
        assert heatmap.width == evidence.width

    def test_engine_extract_regions(self) -> None:
        """Test engine method for region extraction."""
        engine = EvidenceOverlayEngine()
        evidence = engine.generate_stubbed_evidence(width=50, height=50, seed=42)
        heatmap = engine.normalize(evidence)
        regions = engine.extract_regions(heatmap)
        assert isinstance(regions, tuple)

    def test_engine_create_bundle(self) -> None:
        """Test engine method for bundle creation."""
        engine = EvidenceOverlayEngine()
        evidence = engine.generate_stubbed_evidence(width=50, height=50, seed=42)
        bundle = engine.create_bundle(evidence)
        assert bundle.evidence_map == evidence


# =============================================================================
# Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_double_run_equality_evidence_map(self) -> None:
        """Test that evidence map generation is deterministic."""
        e1 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        e2 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        assert e1.values == e2.values

    def test_double_run_equality_heatmap(self) -> None:
        """Test that heatmap normalization is deterministic."""
        e1 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        e2 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        h1 = normalize_evidence_to_heatmap(e1)
        h2 = normalize_evidence_to_heatmap(e2)
        assert h1.values == h2.values

    def test_double_run_equality_regions(self) -> None:
        """Test that region extraction is deterministic."""
        e1 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        h1 = normalize_evidence_to_heatmap(e1)
        r1 = extract_regions_from_heatmap(h1)
        
        e2 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        h2 = normalize_evidence_to_heatmap(e2)
        r2 = extract_regions_from_heatmap(h2)
        
        assert len(r1) == len(r2)
        for reg1, reg2 in zip(r1, r2):
            assert reg1.region_id == reg2.region_id
            assert reg1.x_min == reg2.x_min
            assert reg1.y_min == reg2.y_min
            assert reg1.area == reg2.area

    def test_double_run_equality_bundle(self) -> None:
        """Test that bundle creation is deterministic."""
        e1 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        b1 = create_overlay_bundle(e1)
        
        e2 = generate_stubbed_evidence_map(width=100, height=100, seed=42)
        b2 = create_overlay_bundle(e2)
        
        assert b1.to_dict() == b2.to_dict()


# =============================================================================
# AST Guardrails Tests
# =============================================================================


class TestASTGuardrails:
    """Tests for forbidden import guardrails."""

    def test_no_subprocess_import(self) -> None:
        """Test that evidence_overlay.py has no subprocess import."""
        module_path = Path(__file__).parent.parent / "app" / "clarity" / "evidence_overlay.py"
        with open(module_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "subprocess" not in alias.name, "subprocess import found"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "subprocess" not in node.module, "subprocess import found"

    def test_no_random_import(self) -> None:
        """Test that evidence_overlay.py has no random import."""
        module_path = Path(__file__).parent.parent / "app" / "clarity" / "evidence_overlay.py"
        with open(module_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random", "random import found"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "random" not in node.module, "random import found"

    def test_no_uuid_import(self) -> None:
        """Test that evidence_overlay.py has no uuid import."""
        module_path = Path(__file__).parent.parent / "app" / "clarity" / "evidence_overlay.py"
        with open(module_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "uuid", "uuid import found"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "uuid" not in node.module, "uuid import found"

    def test_no_datetime_now_usage(self) -> None:
        """Test that evidence_overlay.py has no datetime.now usage in code."""
        module_path = Path(__file__).parent.parent / "app" / "clarity" / "evidence_overlay.py"
        with open(module_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        
        # Check for datetime.now() or datetime.utcnow() calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("now", "utcnow"):
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id == "datetime":
                                pytest.fail("datetime.now() or datetime.utcnow() call found")

    def test_no_r2l_import(self) -> None:
        """Test that evidence_overlay.py has no direct r2l import."""
        module_path = Path(__file__).parent.parent / "app" / "clarity" / "evidence_overlay.py"
        with open(module_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "r2l" not in alias.name.lower(), "r2l import found"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "r2l" not in node.module.lower(), "r2l import found"


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_1x1_evidence_map(self) -> None:
        """Test handling of 1x1 evidence map."""
        evidence = generate_stubbed_evidence_map(width=1, height=1, seed=42)
        assert evidence.width == 1
        assert evidence.height == 1
        assert len(evidence.values) == 1
        assert len(evidence.values[0]) == 1

    def test_1x1_heatmap_normalization(self) -> None:
        """Test normalization of 1x1 heatmap."""
        values = ((0.5,),)
        evidence = EvidenceMap(width=1, height=1, values=values)
        heatmap = normalize_evidence_to_heatmap(evidence)
        assert heatmap.width == 1
        assert heatmap.height == 1

    def test_1x1_region_extraction(self) -> None:
        """Test region extraction from 1x1 heatmap."""
        values = ((0.9,),)
        heatmap = Heatmap(width=1, height=1, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 1

    def test_large_evidence_map_performance(self) -> None:
        """Test that large evidence map can be generated."""
        evidence = generate_stubbed_evidence_map(width=500, height=500, seed=42)
        assert evidence.width == 500
        assert evidence.height == 500

    def test_threshold_boundary_exact(self) -> None:
        """Test threshold boundary (value == threshold)."""
        # Values exactly at threshold should NOT be included (> not >=)
        values = ((0.7, 0.7), (0.7, 0.7))
        heatmap = Heatmap(width=2, height=2, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 0

    def test_threshold_boundary_just_above(self) -> None:
        """Test threshold boundary (value just above threshold)."""
        values = ((0.70000001, 0.70000001), (0.70000001, 0.70000001))
        heatmap = Heatmap(width=2, height=2, values=values)
        regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        assert len(regions) == 1

