"""Cache Manager for CLARITY.

M12: Thread-safe caching with atomic writes and file locking.

CRITICAL CONSTRAINTS:
1. Writes must be atomic (temp file → rename).
2. File locks prevent concurrent generation of the same artifact.
3. Lock timeout returns HTTP 409 "in progress".
4. Cache is deterministic - same input always produces same output.
5. No cross-request mutation.
"""

from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generator return type
T = TypeVar("T", bound=bytes)

# Default cache directory (configurable via CLARITY_CACHE_DIR env var)
DEFAULT_CACHE_DIR = Path(__file__).parent.parent.parent.parent.parent / ".clarity_cache"


def get_cache_dir() -> Path:
    """Get the cache directory path.

    Reads from CLARITY_CACHE_DIR environment variable,
    falls back to DEFAULT_CACHE_DIR.

    Returns:
        Path to cache directory.
    """
    env_dir = os.environ.get("CLARITY_CACHE_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_CACHE_DIR


class CacheError(Exception):
    """Base exception for cache errors."""

    pass


class CacheInProgressError(CacheError):
    """Raised when another request is generating the same cache entry.

    This should result in HTTP 409.
    """

    pass


class CacheLockError(CacheError):
    """Raised when unable to acquire a lock."""

    pass


class FileLock:
    """Simple file-based lock for cross-process synchronization.

    Uses a lock file to coordinate access. The lock is released
    when the context manager exits.
    """

    def __init__(self, lock_path: Path, timeout: float = 30.0):
        """Initialize the file lock.

        Args:
            lock_path: Path to the lock file.
            timeout: Maximum time to wait for lock in seconds.
        """
        self.lock_path = lock_path
        self.timeout = timeout
        self._acquired = False

    def __enter__(self) -> "FileLock":
        """Acquire the lock."""
        self.acquire()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Release the lock."""
        self.release()

    def acquire(self) -> None:
        """Acquire the lock, waiting up to timeout seconds.

        Raises:
            CacheInProgressError: If lock is held by another process.
        """
        start_time = time.monotonic()
        poll_interval = 0.1  # 100ms

        # Ensure parent directory exists
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)

        while True:
            try:
                # Attempt to create lock file exclusively
                # os.O_CREAT | os.O_EXCL ensures atomic creation
                fd = os.open(
                    self.lock_path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                # Write PID for debugging
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                self._acquired = True
                logger.debug(f"Acquired lock: {self.lock_path}")
                return
            except FileExistsError:
                # Lock is held by another process
                elapsed = time.monotonic() - start_time
                if elapsed >= self.timeout:
                    logger.warning(
                        f"Lock timeout after {elapsed:.1f}s: {self.lock_path}"
                    )
                    raise CacheInProgressError(
                        f"Cache generation in progress for: {self.lock_path.stem}"
                    )
                time.sleep(poll_interval)

    def release(self) -> None:
        """Release the lock by removing the lock file."""
        if self._acquired:
            try:
                self.lock_path.unlink()
                logger.debug(f"Released lock: {self.lock_path}")
            except FileNotFoundError:
                # Already removed, that's fine
                pass
            self._acquired = False


class CacheManager:
    """Thread-safe cache manager with atomic writes.

    Usage:
        cache = CacheManager()
        pdf_bytes = cache.get_or_create(
            cache_key="abc123",
            generator=lambda: render_report_to_pdf(report),
            extension=".pdf",
        )
    """

    def __init__(self, cache_dir: Path | None = None, lock_timeout: float = 30.0):
        """Initialize the cache manager.

        Args:
            cache_dir: Directory for cache files. Defaults to CLARITY_CACHE_DIR
                       env var or .clarity_cache in repo root.
            lock_timeout: Maximum time to wait for locks in seconds.
        """
        self.cache_dir = cache_dir or get_cache_dir()
        self.lock_timeout = lock_timeout

    def _cache_path(self, cache_key: str, extension: str = "") -> Path:
        """Get the cache file path for a key.

        Args:
            cache_key: The cache key (hash).
            extension: File extension (e.g., ".pdf").

        Returns:
            Path to the cache file.
        """
        return self.cache_dir / f"{cache_key}{extension}"

    def _lock_path(self, cache_key: str) -> Path:
        """Get the lock file path for a key.

        Args:
            cache_key: The cache key (hash).

        Returns:
            Path to the lock file.
        """
        return self.cache_dir / f"{cache_key}.lock"

    def get(self, cache_key: str, extension: str = "") -> bytes | None:
        """Get cached data if it exists.

        Args:
            cache_key: The cache key (hash).
            extension: File extension (e.g., ".pdf").

        Returns:
            Cached bytes if found, None otherwise.
        """
        cache_path = self._cache_path(cache_key, extension)

        if cache_path.exists():
            logger.debug(f"Cache hit: {cache_key}")
            return cache_path.read_bytes()

        logger.debug(f"Cache miss: {cache_key}")
        return None

    def put(self, cache_key: str, data: bytes, extension: str = "") -> Path:
        """Store data in cache with atomic write.

        Uses temp file + rename for atomicity.

        Args:
            cache_key: The cache key (hash).
            data: The data to cache.
            extension: File extension (e.g., ".pdf").

        Returns:
            Path to the cached file.
        """
        cache_path = self._cache_path(cache_key, extension)

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Write to temp file first
        fd, temp_path = tempfile.mkstemp(
            dir=self.cache_dir,
            prefix=f".{cache_key}_",
            suffix=extension,
        )
        try:
            os.write(fd, data)
            os.close(fd)

            # Atomic rename to final location
            # On POSIX this is atomic; on Windows it may not be
            # but os.replace is the closest we get
            os.replace(temp_path, cache_path)
            logger.debug(f"Cached: {cache_key}")
        except Exception:
            # Clean up temp file on error
            try:
                os.close(fd)
            except Exception:
                pass
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise

        return cache_path

    def get_or_create(
        self,
        cache_key: str,
        generator: Callable[[], bytes],
        extension: str = "",
    ) -> bytes:
        """Get cached data or generate and cache it.

        Thread-safe: uses file locks to prevent duplicate generation.

        Args:
            cache_key: The cache key (hash).
            generator: Function that generates the data if not cached.
            extension: File extension (e.g., ".pdf").

        Returns:
            The cached or newly generated data.

        Raises:
            CacheInProgressError: If another process is generating the same entry.
        """
        # Check cache first (no lock needed for read)
        cached = self.get(cache_key, extension)
        if cached is not None:
            return cached

        # Acquire lock for generation
        lock = FileLock(self._lock_path(cache_key), timeout=self.lock_timeout)

        with lock:
            # Double-check after acquiring lock (another process may have finished)
            cached = self.get(cache_key, extension)
            if cached is not None:
                logger.debug(f"Cache populated while waiting: {cache_key}")
                return cached

            # Generate data
            logger.info(f"Generating cache entry: {cache_key}")
            data = generator()

            # Store in cache
            self.put(cache_key, data, extension)

            return data

    def clear(self) -> int:
        """Clear all cached files.

        Returns:
            Number of files removed.
        """
        count = 0
        if self.cache_dir.exists():
            for path in self.cache_dir.iterdir():
                if path.is_file() and not path.name.endswith(".lock"):
                    path.unlink()
                    count += 1
        logger.info(f"Cleared {count} cache entries")
        return count

    def exists(self, cache_key: str, extension: str = "") -> bool:
        """Check if a cache entry exists.

        Args:
            cache_key: The cache key (hash).
            extension: File extension (e.g., ".pdf").

        Returns:
            True if cached, False otherwise.
        """
        return self._cache_path(cache_key, extension).exists()

