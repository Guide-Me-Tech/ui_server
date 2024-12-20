import os
import sys
import time
import logging
import functools
import threading
from typing import Any, Callable, Dict, Optional, Tuple
from collections import OrderedDict

"""
This code provides:
- A caching mechanism (in-memory LRU or Redis-based) for performance optimization.
- Configurable via environment variables for maximum flexibility.
- Metrics for cache hits, misses, evictions to understand caching efficiency.
- An optional admin endpoint integration to flush the cache at runtime.
- Integration with distributed caches like Redis, if configured.
- Easy to adapt and extend for various environments and requirements.
"""

# Step 1: Load environment variables for cache configuration and backend selection
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
CACHE_MAXSIZE = int(os.environ.get("CACHE_MAXSIZE", 100))
CACHE_EXPIRY = int(os.environ.get("CACHE_EXPIRY", 300))
CACHE_BACKEND = os.environ.get("CACHE_BACKEND", "memory")  # "memory" or "redis"
CACHE_LOG_LEVEL = os.environ.get("CACHE_LOG_LEVEL", "ERROR").upper()

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# Step 2: Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(CACHE_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
logger.addHandler(handler)

# Step 3: Metrics for cache operations
# These counters help track the efficiency of the cache.
# They can be integrated with external monitoring by a simple export or endpoint.
cache_metrics = {
    "hits": 0,
    "misses": 0,
    "evictions": 0,
    "expires": 0
}

# Step 4: LRU in-memory cache class
class LRUCache:
    def __init__(self, maxsize: int, expiry: int):
        self.maxsize = maxsize
        self.expiry = expiry
        self.cache: "OrderedDict[Any, Tuple[Any, float]]" = OrderedDict()
        self.lock = threading.Lock()

    def _is_expired(self, timestamp: float) -> bool:
        if self.expiry <= 0:
            return False
        return (time.time() - timestamp) > self.expiry

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                cache_metrics["misses"] += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
            value, ts = self.cache[key]
            if self._is_expired(ts):
                cache_metrics["expires"] += 1
                logger.debug(f"Cache entry expired for key: {key}, evicting")
                del self.cache[key]
                return None
            self.cache.move_to_end(key)
            cache_metrics["hits"] += 1
            logger.debug(f"Cache hit for key: {key}")
            return value

    def set(self, key: Any, value: Any):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            self.cache[key] = (value, time.time())
            self.cache.move_to_end(key)
            if len(self.cache) > self.maxsize:
                oldest_key, _ = self.cache.popitem(last=False)
                cache_metrics["evictions"] += 1
                logger.debug(f"Evicted oldest key due to size limit: {oldest_key}")

    def clear(self):
        with self.lock:
            self.cache.clear()
            logger.debug("Cache cleared")


# Step 5: Redis-based cache (optional)
# If CACHE_BACKEND=redis, we use this class. It requires redis-py installed.
# It mimics the same interface as LRUCache, but stores data in Redis.
# Note: For expiry, we rely on Redis TTL. No local eviction is needed.
# This allows scaling horizontally and integrating with distributed environments.
try:
    import redis
except ImportError:
    redis = None

class RedisCache:
    def __init__(self, maxsize: int, expiry: int, host: str, port: int, db: int):
        self.maxsize = maxsize
        self.expiry = expiry
        if redis is None:
            logger.error("redis-py not installed, cannot use RedisCache.")
            raise RuntimeError("Redis backend requested but redis library not installed.")
        self.client = redis.StrictRedis(host=host, port=port, db=db)
        # We do not implement an LRU in Redis easily. This example uses a simple hash + TTL.
        # For full LRU in Redis, we'd need a more complex strategy.
        # We'll store items as key=hash(key), value=serialized data with timestamp.
        # For demonstration, store JSON or repr. No real LRU eviction here, just TTL-based expiry.
    
    def get(self, key: Any) -> Optional[Any]:
        skey = self._serialize_key(key)
        data = self.client.get(skey)
        if data is None:
            cache_metrics["misses"] += 1
            logger.debug(f"Redis cache miss for key: {key}")
            return None
        # Data is stored as bytes; we can just eval or decode.
        # For safety, assume data is repr(value).
        try:
            value = eval(data.decode('utf-8'))
            cache_metrics["hits"] += 1
            logger.debug(f"Redis cache hit for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Error decoding Redis value for key: {key}: {e}")
            return None

    def set(self, key: Any, value: Any):
        skey = self._serialize_key(key)
        # Store repr(value) for simplicity. Could use JSON if safer.
        val_str = repr(value).encode('utf-8')
        self.client.set(skey, val_str)
        if self.expiry > 0:
            self.client.expire(skey, self.expiry)
        # No LRU eviction in basic Redis mode, rely on expiry and external tools or memory limits.
        # If needed, implement a logic for keys counting and removing oldest. Not trivial with Redis without extra structures.
        logger.debug(f"Stored key: {key} in Redis cache")

    def clear(self):
        # A simple approach: flush entire Redis DB (careful in production).
        # Alternatively, could store keys in a set and iterate to delete them.
        self.client.flushdb()
        logger.debug("Redis cache cleared")

    def _serialize_key(self, key: Any) -> str:
        # Convert complex key into a string.
        # Use hash-based approach for uniqueness.
        # key is (func.__name__, args, sorted(kwargs)).
        # Just repr key, then hash.
        return "cache:" + str(hash(key))

# Step 6: No-operation cache for disabled caching scenario
class NoOpCache:
    def get(self, key: Any) -> Optional[Any]:
        logger.debug(f"Caching disabled, miss for key: {key}")
        cache_metrics["misses"] += 1
        return None
    def set(self, key: Any, value: Any):
        logger.debug("Caching disabled, not storing value.")
    def clear(self):
        logger.debug("Caching disabled, clear does nothing.")

# Step 7: Choose the appropriate cache backend
if not CACHE_ENABLED:
    global_cache = NoOpCache()
elif CACHE_BACKEND.lower() == "redis":
    # Redis cache
    global_cache = RedisCache(CACHE_MAXSIZE, CACHE_EXPIRY, REDIS_HOST, REDIS_PORT, REDIS_DB)
else:
    # Default LRU in-memory
    global_cache = LRUCache(CACHE_MAXSIZE, CACHE_EXPIRY)

# Step 8: Decorator for caching function results
def cache_function(maxsize: Optional[int] = None, expiry: Optional[int] = None, enabled: Optional[bool] = None, backend: Optional[str] = None):
    """
    Decorator for caching function results.
    Parameters:
    - maxsize: override global maxsize for this function
    - expiry: override global expiry for this function
    - enabled: override global enabled flag
    - backend: override global backend ("memory" or "redis")

    This allows fine-grained tuning per function.
    """
    if enabled is None:
        enabled = CACHE_ENABLED
    if maxsize is None:
        maxsize = CACHE_MAXSIZE
    if expiry is None:
        expiry = CACHE_EXPIRY
    if backend is None:
        backend = CACHE_BACKEND

    if not enabled:
        func_cache = NoOpCache()
    else:
        if backend.lower() == "redis":
            if redis is None:
                logger.error("redis library not installed, cannot use Redis backend for this function.")
                func_cache = NoOpCache()
            else:
                func_cache = RedisCache(maxsize, expiry, REDIS_HOST, REDIS_PORT, REDIS_DB)
        else:
            func_cache = LRUCache(maxsize, expiry)

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Construct cache key
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            result = func_cache.get(key)
            if result is not None:
                logger.debug(f"Used cached result for {func.__name__}, args={args}, kwargs={kwargs}")
                return result
            result = func(*args, **kwargs)
            func_cache.set(key, result)
            logger.debug(f"Computed and cached result for {func.__name__}, args={args}, kwargs={kwargs}")
            return result
        return wrapper
    return decorator

# Step 9: Provide a function to get global cache metrics
def get_cache_metrics() -> Dict[str, int]:
    """
    Return current cache metrics: hits, misses, evictions, expires.
    These metrics help understand caching efficiency and can be integrated into monitoring.
    """
    return dict(cache_metrics)

# Step 10: Provide a function to clear the global cache
def clear_global_cache():
    global_cache.clear()

# Step 11: Integration with CLI or admin endpoint
# For an admin endpoint, assume we have access to a FastAPI app.
# We can write a helper to register an endpoint that flushes the cache and returns metrics.
def register_admin_endpoint(app, cache_instance):
    """
    Registers an admin endpoint /admin/flush_cache to flush the cache and return metrics.
    This integrates with the rest of the application that uses FastAPI.
    """
    @app.post("/admin/flush_cache")
    def flush_cache():
        cache_instance.clear()
        return {
            "message": "Cache flushed successfully.",
            "metrics": get_cache_metrics()
        }

    @app.get("/admin/cache_metrics")
    def cache_metrics_endpoint():
        return get_cache_metrics()

# Step 12: Code is now flexible, easy to integrate with other modules:
# - Switch backend from memory to redis by changing CACHE_BACKEND
# - Adjust CACHE_ENABLED to turn caching on/off
# - Adjust CACHE_MAXSIZE, CACHE_EXPIRY for different loads
# - Integrate with admin endpoints by calling register_admin_endpoint(app, global_cache) in server code
# - Metrics and logs provide deep insights without code modifications.
