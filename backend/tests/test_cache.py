"""Tests for CLARITY Cache Module.

M12: Tests for cache key generation and cache manager.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest import mock

import pytest

from app.clarity.cache import CacheManager, compute_case_hash
from app.clarity.cache.cache_key import (
    _canonical_json,
    _quantize_floats,
    compute_dict_hash,
    compute_hash,
)
from app.clarity.cache.cache_manager import (
    CacheError,
    CacheInProgressError,
    CacheLockError,
    FileLock,
    get_cache_dir,
)


# ===========================================================================
# Cache Key Tests
# ===========================================================================


class TestQuantizeFloats:
    """Tests for _quantize_floats function."""

    def test_quantize_float(self):
        """Test single float quantization."""
        assert _quantize_floats(0.123456789, 8) == 0.12345679

    def test_quantize_float_default_decimals(self):
        """Test default 8 decimal places."""
        assert _quantize_floats(0.123456789012) == 0.12345679

    def test_quantize_zero(self):
        """Test zero remains zero."""
        assert _quantize_floats(0.0) == 0.0

    def test_quantize_integer_unchanged(self):
        """Test integers are unchanged."""
        assert _quantize_floats(42) == 42

    def test_quantize_string_unchanged(self):
        """Test strings are unchanged."""
        assert _quantize_floats("hello") == "hello"

    def test_quantize_none_unchanged(self):
        """Test None is unchanged."""
        assert _quantize_floats(None) is None

    def test_quantize_dict(self):
        """Test dictionary values are quantized."""
        data = {"a": 0.123456789, "b": "text", "c": 42}
        result = _quantize_floats(data)
        assert result == {"a": 0.12345679, "b": "text", "c": 42}

    def test_quantize_list(self):
        """Test list values are quantized."""
        data = [0.123456789, "text", 42]
        result = _quantize_floats(data)
        assert result == [0.12345679, "text", 42]

    def test_quantize_nested_structure(self):
        """Test nested structures are quantized."""
        data = {
            "values": [0.123456789, 0.987654321],
            "nested": {"deep": 0.111111111},
        }
        result = _quantize_floats(data)
        assert result["values"] == [0.12345679, 0.98765432]
        assert result["nested"]["deep"] == 0.11111111

    def test_quantize_tuple(self):
        """Test tuples are converted to lists and quantized."""
        data = (0.123456789, 0.987654321)
        result = _quantize_floats(data)
        assert result == [0.12345679, 0.98765432]


class TestCanonicalJson:
    """Tests for _canonical_json function."""

    def test_sorted_keys(self):
        """Test keys are sorted."""
        data = {"z": 1, "a": 2, "m": 3}
        result = _canonical_json(data)
        # Keys should appear in alphabetical order
        assert result.index('"a"') < result.index('"m"') < result.index('"z"')

    def test_no_whitespace(self):
        """Test no extra whitespace."""
        data = {"key": "value"}
        result = _canonical_json(data)
        assert " " not in result
        assert "\n" not in result

    def test_quantized_floats(self):
        """Test floats are quantized."""
        data = {"value": 0.123456789012}
        result = _canonical_json(data)
        # Should be quantized to 8 decimals
        assert "0.12345679" in result

    def test_deterministic(self):
        """Test same input produces same output."""
        data = {"b": 2, "a": 1}
        result1 = _canonical_json(data)
        result2 = _canonical_json(data)
        assert result1 == result2


class TestComputeHash:
    """Tests for compute_hash function."""

    def test_hash_string(self):
        """Test hashing a string."""
        result = compute_hash("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_hash_bytes(self):
        """Test hashing bytes."""
        result = compute_hash(b"hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_hash_deterministic(self):
        """Test same input produces same hash."""
        result1 = compute_hash("test data")
        result2 = compute_hash("test data")
        assert result1 == result2

    def test_hash_different_input_different_output(self):
        """Test different inputs produce different hashes."""
        result1 = compute_hash("data1")
        result2 = compute_hash("data2")
        assert result1 != result2


class TestComputeDictHash:
    """Tests for compute_dict_hash function."""

    def test_hash_dict(self):
        """Test hashing a dictionary."""
        data = {"key": "value"}
        result = compute_dict_hash(data)
        assert len(result) == 64  # SHA256 hex length

    def test_deterministic_key_order(self):
        """Test key order doesn't affect hash."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}
        assert compute_dict_hash(data1) == compute_dict_hash(data2)

    def test_float_quantization(self):
        """Test floats with minor differences hash the same after quantization."""
        data1 = {"value": 0.12345678901}
        data2 = {"value": 0.12345678902}
        # Both should quantize to 0.12345679
        assert compute_dict_hash(data1) == compute_dict_hash(data2)


class TestComputeCaseHash:
    """Tests for compute_case_hash function."""

    @pytest.fixture
    def case_dir(self, tmp_path: Path) -> Path:
        """Create a case directory with test artifacts."""
        case = tmp_path / "test_case"
        case.mkdir()

        # Create required files
        (case / "manifest.json").write_text('{"title": "Test Case"}')
        (case / "metrics.json").write_text('{"esi": 0.95}')
        (case / "overlay_bundle.json").write_text('{"regions": []}')

        return case

    def test_compute_hash_success(self, case_dir: Path):
        """Test successful hash computation."""
        result = compute_case_hash(case_dir)
        assert len(result) == 64  # SHA256 hex length

    def test_hash_deterministic(self, case_dir: Path):
        """Test same case produces same hash."""
        result1 = compute_case_hash(case_dir)
        result2 = compute_case_hash(case_dir)
        assert result1 == result2

    def test_hash_changes_with_content(self, case_dir: Path):
        """Test hash changes when content changes."""
        result1 = compute_case_hash(case_dir)

        # Modify manifest
        (case_dir / "manifest.json").write_text('{"title": "Modified"}')

        result2 = compute_case_hash(case_dir)
        assert result1 != result2

    def test_missing_manifest(self, tmp_path: Path):
        """Test error when manifest.json is missing."""
        case = tmp_path / "incomplete_case"
        case.mkdir()
        (case / "metrics.json").write_text("{}")
        (case / "overlay_bundle.json").write_text("{}")

        with pytest.raises(FileNotFoundError, match="manifest.json"):
            compute_case_hash(case)

    def test_missing_metrics(self, tmp_path: Path):
        """Test error when metrics.json is missing."""
        case = tmp_path / "incomplete_case"
        case.mkdir()
        (case / "manifest.json").write_text("{}")
        (case / "overlay_bundle.json").write_text("{}")

        with pytest.raises(FileNotFoundError, match="metrics.json"):
            compute_case_hash(case)

    def test_missing_overlay(self, tmp_path: Path):
        """Test error when overlay_bundle.json is missing."""
        case = tmp_path / "incomplete_case"
        case.mkdir()
        (case / "manifest.json").write_text("{}")
        (case / "metrics.json").write_text("{}")

        with pytest.raises(FileNotFoundError, match="overlay_bundle.json"):
            compute_case_hash(case)

    def test_invalid_json(self, tmp_path: Path):
        """Test error when file contains invalid JSON."""
        case = tmp_path / "bad_case"
        case.mkdir()
        (case / "manifest.json").write_text("not valid json")
        (case / "metrics.json").write_text("{}")
        (case / "overlay_bundle.json").write_text("{}")

        with pytest.raises(json.JSONDecodeError):
            compute_case_hash(case)


# ===========================================================================
# Cache Manager Tests
# ===========================================================================


class TestGetCacheDir:
    """Tests for get_cache_dir function."""

    def test_default_cache_dir(self):
        """Test default cache directory."""
        with mock.patch.dict(os.environ, {}, clear=True):
            if "CLARITY_CACHE_DIR" in os.environ:
                del os.environ["CLARITY_CACHE_DIR"]
            result = get_cache_dir()
            assert result.name == ".clarity_cache"

    def test_env_override(self, tmp_path: Path):
        """Test environment variable override."""
        with mock.patch.dict(os.environ, {"CLARITY_CACHE_DIR": str(tmp_path)}):
            result = get_cache_dir()
            assert result == tmp_path


class TestFileLock:
    """Tests for FileLock class."""

    def test_acquire_release(self, tmp_path: Path):
        """Test basic acquire and release."""
        lock_path = tmp_path / "test.lock"
        lock = FileLock(lock_path)

        lock.acquire()
        assert lock_path.exists()

        lock.release()
        assert not lock_path.exists()

    def test_context_manager(self, tmp_path: Path):
        """Test context manager interface."""
        lock_path = tmp_path / "test.lock"

        with FileLock(lock_path) as lock:
            assert lock_path.exists()

        assert not lock_path.exists()

    def test_double_release_safe(self, tmp_path: Path):
        """Test double release doesn't raise."""
        lock_path = tmp_path / "test.lock"
        lock = FileLock(lock_path)

        lock.acquire()
        lock.release()
        lock.release()  # Should not raise

    def test_timeout_raises(self, tmp_path: Path):
        """Test timeout raises CacheInProgressError."""
        lock_path = tmp_path / "test.lock"

        # Create lock file manually
        lock_path.write_text("12345")

        lock = FileLock(lock_path, timeout=0.5)

        with pytest.raises(CacheInProgressError, match="in progress"):
            lock.acquire()

    def test_creates_parent_directory(self, tmp_path: Path):
        """Test lock creates parent directory if needed."""
        lock_path = tmp_path / "deep" / "nested" / "test.lock"
        lock = FileLock(lock_path)

        lock.acquire()
        assert lock_path.exists()
        lock.release()


class TestCacheManager:
    """Tests for CacheManager class."""

    @pytest.fixture
    def cache(self, tmp_path: Path) -> CacheManager:
        """Create a CacheManager with temp directory."""
        return CacheManager(cache_dir=tmp_path)

    def test_put_and_get(self, cache: CacheManager):
        """Test basic put and get."""
        cache.put("testkey", b"test data")
        result = cache.get("testkey")
        assert result == b"test data"

    def test_get_missing_returns_none(self, cache: CacheManager):
        """Test get returns None for missing key."""
        result = cache.get("nonexistent")
        assert result is None

    def test_exists_true(self, cache: CacheManager):
        """Test exists returns True for cached key."""
        cache.put("testkey", b"data")
        assert cache.exists("testkey")

    def test_exists_false(self, cache: CacheManager):
        """Test exists returns False for missing key."""
        assert not cache.exists("nonexistent")

    def test_put_with_extension(self, cache: CacheManager):
        """Test put with file extension."""
        cache.put("testkey", b"pdf data", extension=".pdf")
        result = cache.get("testkey", extension=".pdf")
        assert result == b"pdf data"

    def test_atomic_write(self, cache: CacheManager, tmp_path: Path):
        """Test write is atomic (no partial files)."""
        large_data = b"x" * 1_000_000  # 1MB
        cache.put("largekey", large_data)

        # File should be complete
        result = cache.get("largekey")
        assert result == large_data

    def test_clear(self, cache: CacheManager):
        """Test clear removes all cache entries."""
        cache.put("key1", b"data1")
        cache.put("key2", b"data2")

        count = cache.clear()
        assert count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_clear_empty_cache(self, cache: CacheManager):
        """Test clear on empty cache returns 0."""
        count = cache.clear()
        assert count == 0


class TestCacheManagerGetOrCreate:
    """Tests for CacheManager.get_or_create method."""

    @pytest.fixture
    def cache(self, tmp_path: Path) -> CacheManager:
        """Create a CacheManager with temp directory."""
        return CacheManager(cache_dir=tmp_path, lock_timeout=5.0)

    def test_generates_on_miss(self, cache: CacheManager):
        """Test generator is called on cache miss."""
        generator_called = []

        def generator() -> bytes:
            generator_called.append(True)
            return b"generated data"

        result = cache.get_or_create("key1", generator)
        assert result == b"generated data"
        assert len(generator_called) == 1

    def test_returns_cached_on_hit(self, cache: CacheManager):
        """Test cached data is returned without calling generator."""
        cache.put("key1", b"cached data")
        generator_called = []

        def generator() -> bytes:
            generator_called.append(True)
            return b"generated data"

        result = cache.get_or_create("key1", generator)
        assert result == b"cached data"
        assert len(generator_called) == 0

    def test_caches_generated_data(self, cache: CacheManager):
        """Test generated data is cached for future requests."""
        call_count = [0]

        def generator() -> bytes:
            call_count[0] += 1
            return b"data"

        # First call generates
        cache.get_or_create("key1", generator)
        assert call_count[0] == 1

        # Second call uses cache
        cache.get_or_create("key1", generator)
        assert call_count[0] == 1

    def test_extension_supported(self, cache: CacheManager):
        """Test get_or_create with file extension."""
        result = cache.get_or_create(
            "key1",
            lambda: b"pdf bytes",
            extension=".pdf",
        )
        assert result == b"pdf bytes"

        # Check file has correct extension
        cache_file = cache.cache_dir / "key1.pdf"
        assert cache_file.exists()


class TestCacheManagerConcurrency:
    """Tests for cache manager concurrent access."""

    @pytest.fixture
    def cache(self, tmp_path: Path) -> CacheManager:
        """Create a CacheManager with temp directory."""
        return CacheManager(cache_dir=tmp_path, lock_timeout=10.0)

    def test_concurrent_get_or_create_single_generation(self, cache: CacheManager):
        """Test only one generation occurs for concurrent requests."""
        generation_count = [0]
        generation_lock = threading.Lock()
        results: list[bytes] = []
        errors: list[Exception] = []

        def slow_generator() -> bytes:
            with generation_lock:
                generation_count[0] += 1
            time.sleep(0.5)  # Slow generation
            return b"generated data"

        def worker():
            try:
                result = cache.get_or_create("concurrent_key", slow_generator)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert len(errors) == 0

        # All results should be the same
        assert all(r == b"generated data" for r in results)

        # Only one generation should have occurred
        # (others waited or got cache hit)
        assert generation_count[0] == 1

    def test_parallel_different_keys(self, cache: CacheManager):
        """Test parallel requests with different keys both succeed."""
        results: dict[str, bytes] = {}

        def generator(key: str) -> bytes:
            time.sleep(0.1)
            return f"data for {key}".encode()

        def worker(key: str):
            result = cache.get_or_create(key, lambda: generator(key))
            results[key] = result

        t1 = threading.Thread(target=worker, args=("key1",))
        t2 = threading.Thread(target=worker, args=("key2",))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert results["key1"] == b"data for key1"
        assert results["key2"] == b"data for key2"

    def test_no_partial_files(self, cache: CacheManager):
        """Test no partial files are visible during concurrent writes."""
        large_data = b"x" * 100_000
        all_complete = [True]

        def check_data():
            """Check that if file exists, it's complete."""
            for _ in range(100):
                data = cache.get("check_key")
                if data is not None and len(data) != len(large_data):
                    all_complete[0] = False
                time.sleep(0.001)

        def write_data():
            cache.put("check_key", large_data)

        checker = threading.Thread(target=check_data)
        writer = threading.Thread(target=write_data)

        checker.start()
        time.sleep(0.01)  # Let checker start
        writer.start()

        checker.join()
        writer.join()

        assert all_complete[0], "Partial file was visible"


# ===========================================================================
# Integration Tests
# ===========================================================================


class TestCacheIntegration:
    """Integration tests for the cache module."""

    @pytest.fixture
    def case_dir(self, tmp_path: Path) -> Path:
        """Create a case directory with test artifacts."""
        case = tmp_path / "case_001"
        case.mkdir()

        (case / "manifest.json").write_text(
            json.dumps({"title": "Test Case", "version": "1.0"})
        )
        (case / "metrics.json").write_text(
            json.dumps({"esi": 0.95, "drift": 0.02})
        )
        (case / "overlay_bundle.json").write_text(
            json.dumps({"regions": [{"id": "r1", "area": 0.1}]})
        )

        return case

    def test_end_to_end_caching(self, tmp_path: Path, case_dir: Path):
        """Test full caching workflow."""
        cache = CacheManager(cache_dir=tmp_path / "cache")
        cache_key = compute_case_hash(case_dir)

        # First request generates
        call_count = [0]

        def generator() -> bytes:
            call_count[0] += 1
            return b"PDF CONTENT"

        result1 = cache.get_or_create(cache_key, generator, extension=".pdf")
        assert result1 == b"PDF CONTENT"
        assert call_count[0] == 1

        # Second request uses cache
        result2 = cache.get_or_create(cache_key, generator, extension=".pdf")
        assert result2 == b"PDF CONTENT"
        assert call_count[0] == 1  # No additional call

    def test_cache_invalidation_on_content_change(
        self, tmp_path: Path, case_dir: Path
    ):
        """Test different cache keys for different content."""
        cache = CacheManager(cache_dir=tmp_path / "cache")

        # Get initial hash
        hash1 = compute_case_hash(case_dir)

        # Modify manifest
        (case_dir / "manifest.json").write_text(
            json.dumps({"title": "Modified Case", "version": "2.0"})
        )

        # Get new hash
        hash2 = compute_case_hash(case_dir)

        # Hashes should differ
        assert hash1 != hash2

