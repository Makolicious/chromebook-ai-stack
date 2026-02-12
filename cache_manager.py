"""
MAiKO Cache Manager
Response caching for improved performance and cost reduction
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
import hashlib
import json
import time
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract cache backend"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        """Set value in cache"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear entire cache"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass


class InMemoryCacheBackend(CacheBackend):
    """In-memory cache backend (for development)"""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, tuple] = {}  # (value, expiry_time)
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None

        value, expiry = self.cache[key]
        if expiry and time.time() > expiry:
            del self.cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = list(self.cache.keys())[0]
            del self.cache[oldest_key]

        expiry = None
        if ttl_seconds:
            expiry = time.time() + ttl_seconds

        self.cache[key] = (value, expiry)
        return True

    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> bool:
        self.cache.clear()
        return True

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


class FileCacheBackend(CacheBackend):
    """File-based cache backend"""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def get(self, key: str) -> Optional[Any]:
        try:
            path = self._get_path(key)
            if not os.path.exists(path):
                return None

            with open(path, 'r') as f:
                data = json.load(f)

            # Check expiry
            if data.get('expiry') and time.time() > data['expiry']:
                os.remove(path)
                return None

            return data.get('value')

        except Exception as e:
            logger.error(f"Failed to read from cache: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        try:
            path = self._get_path(key)
            data = {
                'key': key,
                'value': value,
                'timestamp': time.time(),
                'expiry': time.time() + ttl_seconds if ttl_seconds else None
            }

            with open(path, 'w') as f:
                json.dump(data, f)

            return True

        except Exception as e:
            logger.error(f"Failed to write to cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        try:
            path = self._get_path(key)
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete from cache: {e}")
            return False

    def clear(self) -> bool:
        try:
            for f in os.listdir(self.cache_dir):
                if f.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, f))
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


class CacheManager:
    """High-level cache management"""

    def __init__(self, backend: CacheBackend = None):
        self.backend = backend or InMemoryCacheBackend()

    def get_cached_or_compute(
        self,
        key: str,
        compute_fn,
        ttl_seconds: int = 3600
    ) -> Any:
        """Get from cache or compute if not cached"""
        cached = self.backend.get(key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached

        logger.debug(f"Cache miss for key: {key}, computing...")
        value = compute_fn()
        self.backend.set(key, value, ttl_seconds)
        return value

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        # This is a placeholder - full pattern support depends on backend
        logger.info(f"Invalidating cache pattern: {pattern}")
        return 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "backend_type": self.backend.__class__.__name__,
            "timestamp": datetime.now().isoformat(),
        }


# Default cache manager instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get or create the cache manager"""
    global _cache_manager
    if _cache_manager is None:
        backend_type = os.getenv("CACHE_BACKEND", "memory")
        if backend_type == "file":
            backend = FileCacheBackend(os.getenv("CACHE_DIR", ".cache"))
        else:
            backend = InMemoryCacheBackend()
        _cache_manager = CacheManager(backend)
    return _cache_manager
