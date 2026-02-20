"""Tests for CLARITY Perturbation Module.

Comprehensive test suite covering:
- Determinism (same inputs → same outputs)
- No input mutation
- Hash stability
- Manifest serialization
- Registry functionality
- Parameter validation
- AST guardrails (no forbidden imports)

Target: 20-30 tests with ≥90% coverage on perturbation module.
"""

import ast
import hashlib
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.clarity.image_utils import (
    CANONICAL_MODE,
    SUPPORTED_MODES,
    canonicalize_image,
    float32_to_image,
    image_sha256,
    image_to_float32,
)
from app.clarity.perturbation_registry import (
    DuplicateRegistrationError,
    _REGISTRY,
    clear_registry,
    get_perturbation,
    list_perturbations,
    register_perturbation,
    _initialize_default_registry,
)
from app.clarity.perturbations import (
    BrightnessPerturbation,
    ContrastPerturbation,
    GaussianBlurPerturbation,
    GaussianNoisePerturbation,
    InterpolationMode,
    Perturbation,
    ResizePerturbation,
)


# =============================================================================
# Test Fixtures: Synthetic Images
# =============================================================================


@pytest.fixture
def solid_color_image() -> Image.Image:
    """Create a solid red RGB image."""
    return Image.new("RGB", (100, 100), color=(255, 0, 0))


@pytest.fixture
def gradient_image() -> Image.Image:
    """Create a horizontal gradient image."""
    width, height = 100, 100
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        intensity = int(255 * x / (width - 1))
        arr[:, x, :] = intensity
    return Image.fromarray(arr, mode="RGB")


@pytest.fixture
def checkerboard_image() -> Image.Image:
    """Create a high-frequency checkerboard pattern."""
    width, height = 100, 100
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            if (x // 10 + y // 10) % 2 == 0:
                arr[y, x] = [255, 255, 255]
            else:
                arr[y, x] = [0, 0, 0]
    return Image.fromarray(arr, mode="RGB")


@pytest.fixture
def rgba_image() -> Image.Image:
    """Create an RGBA image with partial transparency."""
    arr = np.zeros((50, 50, 4), dtype=np.uint8)
    arr[:, :, 0] = 255  # Red channel
    arr[:, :, 3] = 128  # 50% alpha
    return Image.fromarray(arr, mode="RGBA")


@pytest.fixture
def grayscale_image() -> Image.Image:
    """Create a grayscale image."""
    arr = np.linspace(0, 255, 100 * 100, dtype=np.uint8).reshape(100, 100)
    return Image.fromarray(arr, mode="L")


# =============================================================================
# Image Utils Tests
# =============================================================================


class TestCanonicalizeImage:
    """Tests for canonicalize_image function."""

    def test_rgb_mode_returned_as_rgb(self, solid_color_image: Image.Image) -> None:
        """RGB input returns RGB output."""
        result = canonicalize_image(solid_color_image)
        assert result.mode == CANONICAL_MODE

    def test_rgb_mode_is_copied(self, solid_color_image: Image.Image) -> None:
        """RGB input is copied, not returned directly."""
        result = canonicalize_image(solid_color_image)
        assert result is not solid_color_image

    def test_grayscale_converted_to_rgb(self, grayscale_image: Image.Image) -> None:
        """Grayscale (L) input is converted to RGB."""
        result = canonicalize_image(grayscale_image)
        assert result.mode == CANONICAL_MODE
        assert result.size == grayscale_image.size

    def test_rgba_composited_on_black(self, rgba_image: Image.Image) -> None:
        """RGBA input is composited onto black background."""
        result = canonicalize_image(rgba_image)
        assert result.mode == CANONICAL_MODE

        # Check that the red channel is dimmed (50% alpha on black = 127)
        arr = np.array(result)
        # Red should be approximately 127 (128 alpha * 255 / 255)
        assert np.mean(arr[:, :, 0]) == pytest.approx(127, abs=2)

    def test_unsupported_mode_raises(self) -> None:
        """Unsupported mode raises ValueError."""
        # Create a CMYK image (unsupported)
        cmyk_image = Image.new("CMYK", (10, 10))
        with pytest.raises(ValueError, match="Unsupported image mode"):
            canonicalize_image(cmyk_image)


class TestImageSha256:
    """Tests for image_sha256 function."""

    def test_same_image_same_hash(self, solid_color_image: Image.Image) -> None:
        """Identical images produce identical hashes."""
        hash1 = image_sha256(solid_color_image)
        hash2 = image_sha256(solid_color_image)
        assert hash1 == hash2

    def test_hash_is_64_char_hex(self, solid_color_image: Image.Image) -> None:
        """Hash is a 64-character lowercase hex string."""
        hash_val = image_sha256(solid_color_image)
        assert len(hash_val) == 64
        assert hash_val == hash_val.lower()
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_different_images_different_hash(
        self, solid_color_image: Image.Image, gradient_image: Image.Image
    ) -> None:
        """Different images produce different hashes."""
        hash1 = image_sha256(solid_color_image)
        hash2 = image_sha256(gradient_image)
        assert hash1 != hash2

    def test_hash_includes_dimensions(self) -> None:
        """Same pixel data but different dimensions → different hash."""
        # Create two images with same total bytes but different dimensions
        img1 = Image.new("RGB", (100, 50), color=(128, 128, 128))
        img2 = Image.new("RGB", (50, 100), color=(128, 128, 128))

        hash1 = image_sha256(img1)
        hash2 = image_sha256(img2)
        assert hash1 != hash2

    def test_hash_stability_across_calls(
        self, checkerboard_image: Image.Image
    ) -> None:
        """Hash is stable across multiple calls."""
        hashes = [image_sha256(checkerboard_image) for _ in range(10)]
        assert len(set(hashes)) == 1  # All identical


class TestImageConversion:
    """Tests for image_to_float32 and float32_to_image."""

    def test_roundtrip_preserves_image(self, gradient_image: Image.Image) -> None:
        """Converting to float32 and back preserves the image."""
        arr = image_to_float32(gradient_image)
        result = float32_to_image(arr)

        original_arr = np.array(gradient_image)
        result_arr = np.array(result)
        np.testing.assert_array_equal(original_arr, result_arr)

    def test_float32_range_is_normalized(
        self, solid_color_image: Image.Image
    ) -> None:
        """Float32 array values are in [0, 1] range."""
        arr = image_to_float32(solid_color_image)
        assert arr.dtype == np.float32
        assert arr.min() >= 0.0
        assert arr.max() <= 1.0

    def test_float32_to_image_clips_values(self) -> None:
        """Values outside [0, 1] are clipped."""
        arr = np.array([[-0.5, 0.5], [1.5, 0.5]], dtype=np.float32)
        arr = np.stack([arr, arr, arr], axis=-1)  # Make RGB

        result = float32_to_image(arr)
        result_arr = np.array(result)

        # Check clipping: -0.5 → 0, 1.5 → 255
        assert result_arr[0, 0, 0] == 0
        assert result_arr[1, 0, 0] == 255


# =============================================================================
# Perturbation Tests: Brightness
# =============================================================================


class TestBrightnessPerturbation:
    """Tests for BrightnessPerturbation."""

    def test_factor_one_no_change(self, solid_color_image: Image.Image) -> None:
        """Factor 1.0 produces visually identical output."""
        pert = BrightnessPerturbation(factor=1.0)
        result = pert.apply(solid_color_image)

        # Hash should be same (or very close for PIL operations)
        original_hash = image_sha256(solid_color_image)
        result_hash = image_sha256(result)
        assert original_hash == result_hash

    def test_factor_zero_produces_black(
        self, solid_color_image: Image.Image
    ) -> None:
        """Factor 0.0 produces a black image."""
        pert = BrightnessPerturbation(factor=0.0)
        result = pert.apply(solid_color_image)

        arr = np.array(result)
        assert np.all(arr == 0)

    def test_determinism(self, gradient_image: Image.Image) -> None:
        """Same parameters produce byte-identical output."""
        pert1 = BrightnessPerturbation(factor=0.7)
        pert2 = BrightnessPerturbation(factor=0.7)

        result1 = pert1.apply(gradient_image)
        result2 = pert2.apply(gradient_image)

        assert image_sha256(result1) == image_sha256(result2)

    def test_negative_factor_raises(self) -> None:
        """Negative factor raises ValueError."""
        with pytest.raises(ValueError, match="factor must be >= 0.0"):
            BrightnessPerturbation(factor=-0.5)

    def test_invalid_type_raises(self) -> None:
        """Non-numeric factor raises TypeError."""
        with pytest.raises(TypeError, match="factor must be a number"):
            BrightnessPerturbation(factor="bright")  # type: ignore

    def test_manifest_dict(self) -> None:
        """to_manifest_dict returns correct structure."""
        pert = BrightnessPerturbation(factor=1.5)
        manifest = pert.to_manifest_dict()

        assert manifest["name"] == "brightness"
        assert manifest["version"] == "1.0.0"
        assert manifest["params"]["factor"] == 1.5

    def test_immutability(self) -> None:
        """Perturbation is immutable (frozen dataclass)."""
        pert = BrightnessPerturbation(factor=1.0)
        with pytest.raises(AttributeError):
            pert.factor = 2.0  # type: ignore

    def test_output_is_rgb(self, grayscale_image: Image.Image) -> None:
        """Output is always RGB mode."""
        pert = BrightnessPerturbation(factor=1.0)
        result = pert.apply(grayscale_image)
        assert result.mode == "RGB"


# =============================================================================
# Perturbation Tests: Contrast
# =============================================================================


class TestContrastPerturbation:
    """Tests for ContrastPerturbation."""

    def test_factor_one_no_change(self, gradient_image: Image.Image) -> None:
        """Factor 1.0 produces identical output."""
        pert = ContrastPerturbation(factor=1.0)
        result = pert.apply(gradient_image)

        assert image_sha256(gradient_image) == image_sha256(result)

    def test_determinism(self, checkerboard_image: Image.Image) -> None:
        """Same parameters produce byte-identical output."""
        pert = ContrastPerturbation(factor=1.5)

        results = [pert.apply(checkerboard_image) for _ in range(5)]
        hashes = [image_sha256(r) for r in results]

        assert len(set(hashes)) == 1

    def test_manifest_dict(self) -> None:
        """to_manifest_dict returns correct structure."""
        pert = ContrastPerturbation(factor=2.0)
        manifest = pert.to_manifest_dict()

        assert manifest["name"] == "contrast"
        assert manifest["version"] == "1.0.0"
        assert manifest["params"]["factor"] == 2.0


# =============================================================================
# Perturbation Tests: Gaussian Noise
# =============================================================================


class TestGaussianNoisePerturbation:
    """Tests for GaussianNoisePerturbation."""

    def test_same_seed_same_output(self, solid_color_image: Image.Image) -> None:
        """Same seed produces byte-identical output."""
        pert1 = GaussianNoisePerturbation(std_dev=0.1, seed=42)
        pert2 = GaussianNoisePerturbation(std_dev=0.1, seed=42)

        result1 = pert1.apply(solid_color_image)
        result2 = pert2.apply(solid_color_image)

        assert image_sha256(result1) == image_sha256(result2)

    def test_different_seed_different_output(
        self, solid_color_image: Image.Image
    ) -> None:
        """Different seeds produce different outputs."""
        pert1 = GaussianNoisePerturbation(std_dev=0.1, seed=42)
        pert2 = GaussianNoisePerturbation(std_dev=0.1, seed=43)

        result1 = pert1.apply(solid_color_image)
        result2 = pert2.apply(solid_color_image)

        assert image_sha256(result1) != image_sha256(result2)

    def test_zero_std_dev_no_change(self, gradient_image: Image.Image) -> None:
        """Zero std_dev produces identical output."""
        pert = GaussianNoisePerturbation(std_dev=0.0, seed=42)
        result = pert.apply(gradient_image)

        assert image_sha256(gradient_image) == image_sha256(result)

    def test_std_dev_out_of_range_raises(self) -> None:
        """std_dev outside [0.0, 1.0] raises ValueError."""
        with pytest.raises(ValueError, match="std_dev must be in"):
            GaussianNoisePerturbation(std_dev=1.5, seed=42)

        with pytest.raises(ValueError, match="std_dev must be in"):
            GaussianNoisePerturbation(std_dev=-0.1, seed=42)

    def test_seed_required(self) -> None:
        """Seed parameter is required."""
        with pytest.raises(TypeError):
            GaussianNoisePerturbation(std_dev=0.1)  # type: ignore

    def test_seed_must_be_int(self) -> None:
        """Seed must be an integer."""
        with pytest.raises(TypeError, match="seed must be an int"):
            GaussianNoisePerturbation(std_dev=0.1, seed=42.5)  # type: ignore

    def test_manifest_dict(self) -> None:
        """to_manifest_dict returns correct structure."""
        pert = GaussianNoisePerturbation(std_dev=0.2, seed=12345)
        manifest = pert.to_manifest_dict()

        assert manifest["name"] == "gaussian_noise"
        assert manifest["version"] == "1.0.0"
        assert manifest["params"]["std_dev"] == 0.2
        assert manifest["params"]["seed"] == 12345


# =============================================================================
# Perturbation Tests: Gaussian Blur
# =============================================================================


class TestGaussianBlurPerturbation:
    """Tests for GaussianBlurPerturbation."""

    def test_zero_radius_no_change(self, gradient_image: Image.Image) -> None:
        """Radius 0 produces identical output."""
        pert = GaussianBlurPerturbation(radius=0)
        result = pert.apply(gradient_image)

        assert image_sha256(gradient_image) == image_sha256(result)

    def test_determinism(self, checkerboard_image: Image.Image) -> None:
        """Same radius produces byte-identical output."""
        pert = GaussianBlurPerturbation(radius=2.0)

        results = [pert.apply(checkerboard_image) for _ in range(5)]
        hashes = [image_sha256(r) for r in results]

        assert len(set(hashes)) == 1

    def test_negative_radius_raises(self) -> None:
        """Negative radius raises ValueError."""
        with pytest.raises(ValueError, match="radius must be >= 0"):
            GaussianBlurPerturbation(radius=-1.0)

    def test_manifest_dict(self) -> None:
        """to_manifest_dict returns correct structure."""
        pert = GaussianBlurPerturbation(radius=3.5)
        manifest = pert.to_manifest_dict()

        assert manifest["name"] == "gaussian_blur"
        assert manifest["version"] == "1.0.0"
        assert manifest["params"]["radius"] == 3.5


# =============================================================================
# Perturbation Tests: Resize
# =============================================================================


class TestResizePerturbation:
    """Tests for ResizePerturbation."""

    def test_resize_changes_dimensions(
        self, solid_color_image: Image.Image
    ) -> None:
        """Resize changes image dimensions."""
        pert = ResizePerturbation(width=50, height=25)
        result = pert.apply(solid_color_image)

        assert result.size == (50, 25)

    def test_determinism(self, gradient_image: Image.Image) -> None:
        """Same parameters produce byte-identical output."""
        pert = ResizePerturbation(width=200, height=150)

        results = [pert.apply(gradient_image) for _ in range(5)]
        hashes = [image_sha256(r) for r in results]

        assert len(set(hashes)) == 1

    def test_interpolation_modes(self, checkerboard_image: Image.Image) -> None:
        """Different interpolation modes produce different results."""
        hashes = []
        for mode in InterpolationMode:
            pert = ResizePerturbation(width=50, height=50, interpolation=mode)
            result = pert.apply(checkerboard_image)
            hashes.append(image_sha256(result))

        # At least some modes should differ
        assert len(set(hashes)) > 1

    def test_default_interpolation_is_bilinear(self) -> None:
        """Default interpolation is BILINEAR."""
        pert = ResizePerturbation(width=50, height=50)
        assert pert.interpolation == InterpolationMode.BILINEAR

    def test_string_interpolation_accepted(self) -> None:
        """String interpolation mode is accepted and converted."""
        pert = ResizePerturbation(width=50, height=50, interpolation="lanczos")  # type: ignore
        assert pert.interpolation == InterpolationMode.LANCZOS

    def test_invalid_interpolation_raises(self) -> None:
        """Invalid interpolation mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid interpolation mode"):
            ResizePerturbation(width=50, height=50, interpolation="invalid")  # type: ignore

    def test_zero_dimensions_raises(self) -> None:
        """Zero or negative dimensions raise ValueError."""
        with pytest.raises(ValueError, match="width must be > 0"):
            ResizePerturbation(width=0, height=50)

        with pytest.raises(ValueError, match="height must be > 0"):
            ResizePerturbation(width=50, height=-10)

    def test_manifest_dict(self) -> None:
        """to_manifest_dict returns correct structure."""
        pert = ResizePerturbation(
            width=200, height=100, interpolation=InterpolationMode.BICUBIC
        )
        manifest = pert.to_manifest_dict()

        assert manifest["name"] == "resize"
        assert manifest["version"] == "1.0.0"
        assert manifest["params"]["width"] == 200
        assert manifest["params"]["height"] == 100
        assert manifest["params"]["interpolation"] == "bicubic"


# =============================================================================
# No Input Mutation Tests
# =============================================================================


class TestNoInputMutation:
    """Guardrail tests verifying perturbations don't mutate input."""

    @pytest.mark.parametrize(
        "perturbation",
        [
            BrightnessPerturbation(factor=0.5),
            ContrastPerturbation(factor=1.5),
            GaussianNoisePerturbation(std_dev=0.1, seed=42),
            GaussianBlurPerturbation(radius=2.0),
            ResizePerturbation(width=50, height=50),
        ],
    )
    def test_input_unchanged_after_apply(
        self, perturbation: Perturbation, gradient_image: Image.Image
    ) -> None:
        """Input image is unchanged after apply()."""
        # Capture original state
        original_hash = image_sha256(gradient_image)
        original_arr = np.array(gradient_image).copy()

        # Apply perturbation
        _ = perturbation.apply(gradient_image)

        # Verify input unchanged
        after_hash = image_sha256(gradient_image)
        after_arr = np.array(gradient_image)

        assert original_hash == after_hash
        np.testing.assert_array_equal(original_arr, after_arr)


# =============================================================================
# Registry Tests
# =============================================================================


class TestPerturbationRegistry:
    """Tests for perturbation_registry module."""

    def test_list_perturbations_returns_all(self) -> None:
        """list_perturbations returns all registered names."""
        names = list_perturbations()

        expected = ["brightness", "contrast", "gaussian_blur", "gaussian_noise", "resize"]
        assert names == expected

    def test_get_perturbation_valid_name(self) -> None:
        """get_perturbation returns correct type."""
        pert = get_perturbation("brightness", factor=1.5)
        assert isinstance(pert, BrightnessPerturbation)
        assert pert.factor == 1.5

    def test_get_perturbation_unknown_name_raises(self) -> None:
        """Unknown name raises KeyError."""
        with pytest.raises(KeyError, match="Unknown perturbation"):
            get_perturbation("nonexistent", param=1)

    def test_get_perturbation_invalid_params_raises(self) -> None:
        """Invalid parameters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid parameters"):
            get_perturbation("brightness", factor=-1.0)

    def test_duplicate_registration_raises(self) -> None:
        """Re-registering same name raises DuplicateRegistrationError."""
        # Registry is already initialized, so brightness is registered
        with pytest.raises(DuplicateRegistrationError, match="already registered"):
            register_perturbation(BrightnessPerturbation)

    def test_clear_and_reinitialize_registry(self) -> None:
        """Registry can be cleared and reinitialized."""
        # Clear registry
        clear_registry()
        assert list_perturbations() == []

        # Reinitialize
        _initialize_default_registry()
        assert len(list_perturbations()) == 5


# =============================================================================
# AST Guardrail Tests
# =============================================================================


class TestASTGuardrails:
    """AST-based tests to prevent forbidden imports."""

    def test_no_random_module_imports_in_perturbations(self) -> None:
        """Perturbation module must not import random module."""
        perturbations_dir = Path(__file__).parent.parent / "app" / "clarity" / "perturbations"

        forbidden_imports = {"random"}

        for py_file in perturbations_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert alias.name not in forbidden_imports, (
                            f"Forbidden import '{alias.name}' found in {py_file.name}"
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module in forbidden_imports:
                        pytest.fail(
                            f"Forbidden import 'from {node.module}' found in {py_file.name}"
                        )

    def test_no_datetime_now_in_perturbations(self) -> None:
        """Perturbation module must not call datetime.now()."""
        perturbations_dir = Path(__file__).parent.parent / "app" / "clarity" / "perturbations"

        for py_file in perturbations_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "now":
                            pytest.fail(
                                f"Forbidden call to 'now()' found in {py_file.name}"
                            )

    def test_no_uuid4_in_perturbations(self) -> None:
        """Perturbation module must not call uuid4()."""
        perturbations_dir = Path(__file__).parent.parent / "app" / "clarity" / "perturbations"

        for py_file in perturbations_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "uuid4":
                            pytest.fail(
                                f"Forbidden call to 'uuid4()' found in {py_file.name}"
                            )
                    elif isinstance(node.func, ast.Name):
                        if node.func.id == "uuid4":
                            pytest.fail(
                                f"Forbidden call to 'uuid4()' found in {py_file.name}"
                            )

    def test_no_global_random_seed_in_perturbations(self) -> None:
        """Perturbation module must not use np.random.seed()."""
        perturbations_dir = Path(__file__).parent.parent / "app" / "clarity" / "perturbations"

        for py_file in perturbations_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")

            # Simple string search for this pattern
            if "np.random.seed" in source or "numpy.random.seed" in source:
                pytest.fail(
                    f"Forbidden 'np.random.seed' found in {py_file.name}"
                )
            if "random.seed" in source:
                pytest.fail(
                    f"Forbidden 'random.seed' found in {py_file.name}"
                )


# =============================================================================
# Repr and Name Tests
# =============================================================================


class TestReprAndProperties:
    """Tests for __repr__ and property methods."""

    def test_repr_is_deterministic(self) -> None:
        """__repr__ produces deterministic output."""
        pert = BrightnessPerturbation(factor=1.5)
        repr1 = repr(pert)
        repr2 = repr(pert)
        assert repr1 == repr2
        # Dataclass repr uses class name, not perturbation name
        assert "BrightnessPerturbation" in repr1
        assert "1.5" in repr1

    def test_name_property(self) -> None:
        """Each perturbation has correct name property."""
        assert BrightnessPerturbation(factor=1.0).name == "brightness"
        assert ContrastPerturbation(factor=1.0).name == "contrast"
        assert GaussianNoisePerturbation(std_dev=0.0, seed=0).name == "gaussian_noise"
        assert GaussianBlurPerturbation(radius=0).name == "gaussian_blur"
        assert ResizePerturbation(width=10, height=10).name == "resize"

    def test_version_property(self) -> None:
        """Each perturbation has version 1.0.0."""
        assert BrightnessPerturbation(factor=1.0).version == "1.0.0"
        assert ContrastPerturbation(factor=1.0).version == "1.0.0"
        assert GaussianNoisePerturbation(std_dev=0.0, seed=0).version == "1.0.0"
        assert GaussianBlurPerturbation(radius=0).version == "1.0.0"
        assert ResizePerturbation(width=10, height=10).version == "1.0.0"

