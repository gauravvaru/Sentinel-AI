import asyncio
import time
from functools import wraps
from typing import Any, Callable, Dict, Tuple

class AsyncTTLCache:
    """
    A concurrency-safe TTL cache for asyncio applications.
    Ensures that multiple concurrent requests for the same key don't trigger
    the expensive underlying computation multiple times (avoids thundering herd).
    """
    def __init__(self, ttl_seconds: int = 30):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self._main_lock = asyncio.Lock()

    async def get_lock(self, key: str) -> asyncio.Lock:
        async with self._main_lock:
            if key not in self.locks:
                self.locks[key] = asyncio.Lock()
            return self.locks[key]

    def _get_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        # Exclude FastAPI dependencies which are typically unhashable or request-specific
        safe_kwargs = {
            k: v for k, v in kwargs.items() 
            if k not in ("session", "request", "background_tasks", "response")
        }
        args_str = str(args)
        kwargs_str = str(sorted(safe_kwargs.items()))
        return f"{func.__name__}:{args_str}:{kwargs_str}"

    def decorator(self):
        def wrapper(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = self._get_key(func, args, kwargs)
                
                # Fast path read
                now = time.time()
                if key in self.cache:
                    val, timestamp = self.cache[key]
                    if now - timestamp < self.ttl:
                        return val

                # Cache miss - acquire lock for this specific key
                lock = await self.get_lock(key)
                async with lock:
                    # Double-checked locking in case another task populated it
                    now = time.time()
                    if key in self.cache:
                        val, timestamp = self.cache[key]
                        if now - timestamp < self.ttl:
                            return val

                    # Compute the value
                    result = await func(*args, **kwargs)
                    
                    # Store in cache
                    self.cache[key] = (result, time.time())
                    return result
            return async_wrapper
        return wrapper

def ttl_cache(ttl_seconds: int = 30):
    """
    Decorator to cache the result of an async function for `ttl_seconds`.
    Safe for concurrent access. Excludes 'session', 'request' from cache key.
    """
    cache_instance = AsyncTTLCache(ttl_seconds=ttl_seconds)
    return cache_instance.decorator()
