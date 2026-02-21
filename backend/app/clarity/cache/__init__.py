"""CLARITY Cache Module.

M12: Provides deterministic caching with concurrency safety.

This module exports:
- compute_case_hash: Generate deterministic cache keys
- CacheManager: Thread-safe cache management with atomic writes
"""

from app.clarity.cache.cache_key import compute_case_hash
from app.clarity.cache.cache_manager import CacheManager

__all__ = ["compute_case_hash", "CacheManager"]

